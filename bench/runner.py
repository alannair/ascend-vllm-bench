"""One-at-a-time bounded benchmark attempts, cleanup, checkpoints, NPU monitoring."""
from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
from .client import measure
from .common import STATE, LOGS, GIB, atomic, load, stamp, utc, csv_open
from .hardware import sample_npus, npu_info
from .runtime import docker_command

STOP=False


class Deadline(RuntimeError):
    pass


def handler(sig, frame):
    global STOP
    if sig==signal.SIGALRM:
        raise Deadline('Run exceeded configured run_timeout_s maximum')
    STOP=True


def stopped():
    return STOP or (STATE/'stop.flag').exists()


def cleanup(name):
    subprocess.run(['docker','rm','-f',name],capture_output=True,text=True,timeout=15)


def free_gib(data_dir):
    return shutil.disk_usage(data_dir).free/GIB


def require_device_state(devices, output):
    for i in devices:
        raw=npu_info(i)
        (output/f'npu_info_{i}.txt').write_text(raw)
        if not Path(f'/dev/davinci{i}').exists():
            raise RuntimeError(f'/dev/davinci{i} is missing')


def unsupported_npu_error(result):
    """Detect Ascend-hard-unsupported model formats from a failed attempt.

    README requires keeping the HF ID and recording the real error; remaining
    configs for that model can fail-fast with the same message.
    """
    text=' '.join(filter(None,[result.get('error'),result.get('traceback')]))
    output=result.get('output')
    if output:
        slog=Path(output)/'server.log'
        if slog.is_file():
            try:
                text+='\n'+slog.read_text()[-8000:]
            except OSError:
                pass
    patterns=('quantization is currently not supported in npu',
              'is currently not supported in npu',
              'auto_awq quantization is currently not supported')
    lowered=text.lower()
    for pat in patterns:
        if pat in lowered:
            for line in text.splitlines():
                if 'not supported' in line.lower() and 'npu' in line.lower():
                    return line.strip()
            return 'quantization/format currently not supported in npu (see server.log)'
    return None


def record_unsupported(item, message, source_output=None):
    output=LOGS/item['model_slug']/item['config_id']/('attempt-'+stamp())
    output.mkdir(parents=True,exist_ok=False)
    if source_output:
        note=(f'Reused unsupported-NPU diagnosis from {source_output}\n{message}\n')
        (output/'server.log').write_text(note)
    result={'run':item,'started_at':utc(),'finished_at':utc(),'elapsed_s':0.0,
            'output':str(output),'status':'failed','error':message,
            'skipped_redundant':True}
    atomic(output/'summary.json',result)
    return result


def run_one(index, item, plan, setup):
    cfg=plan['config']
    output=LOGS/item['model_slug']/item['config_id']/('attempt-'+stamp())
    output.mkdir(parents=True,exist_ok=False)
    name=f'ascend910b3-bench-{plan["plan_id"]}-{index:04d}'
    data_dir=Path(setup['data_dir'])
    cmd=docker_command(cfg,item,output,data_dir,name)
    result={'run':item,'started_at':utc(),'output':str(output),'status':'failed'}
    meta={'run':item,'config':cfg,'docker_command':cmd,'image_id':setup['image_id'],
          'host':setup.get('hardware',{}),'data_dir':str(data_dir),
          'comparison':'CPU REPORT_PINNED.md / NO_RECIPE_REPORT.md exact HF model ID'}
    atomic(output/'config.json',meta)
    stdout=None
    proc=None
    meter_stop=threading.Event()
    meter=None
    started=time.monotonic()
    settings=cfg['measurement']
    signal.setitimer(signal.ITIMER_REAL,int(settings['run_timeout_s']))
    try:
        if stopped():
            raise InterruptedError('Stopped')
        if free_gib(data_dir) < settings['min_storage_free_gib']:
            raise RuntimeError('Insufficient free space before model startup')
        require_device_state(item['devices'],output)
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',cfg['host_port']))==0:
                raise RuntimeError(f'Port {cfg["host_port"]} is occupied')
        stdout=(output/'server.log').open('w',buffering=1)
        # Never log the access token or include it in Docker command arguments.
        env=os.environ.copy()
        token_file=Path('/data2/alan/.hf_token')
        token=token_file.read_text().strip() if token_file.is_file() else env.get('HF_TOKEN','')
        if not token:
            raise RuntimeError('Missing Hugging Face token: /data2/alan/.hf_token')
        env['HF_TOKEN']=token
        env['HUGGING_FACE_HUB_TOKEN']=token
        # Ascend HCCL execute timeout can exceed the default RPC timeout on large loads.
        env.setdefault('VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS','3000')
        token=None
        proc=subprocess.Popen(cmd,cwd=str(data_dir),env=env,
                              stdout=stdout,stderr=subprocess.STDOUT,start_new_session=True)
        env.pop('HF_TOKEN',None)
        env.pop('HUGGING_FACE_HUB_TOKEN',None)
        atomic(STATE/'active.json',{'container':name,'pid':proc.pid,'output':str(output)})
        meter=threading.Thread(target=sample_npus,args=(item['devices'],output,
                          settings['npu_interval_s'],meter_stop),daemon=True)
        meter.start()
        f,w=csv_open(output/'startup_storage.csv',['timestamp_utc','free_gib','elapsed_s'])
        try:
            ready_cap=max(60,int(settings['run_timeout_s'])-int(settings['duration_s'])-int(settings['drain_s'])-60)
            deadline=time.monotonic()+min(int(settings['server_ready_timeout_s']),ready_cap)
            url=f'http://127.0.0.1:{cfg["host_port"]}'
            while time.monotonic()<deadline:
                if stopped():
                    raise InterruptedError('Stopped while loading model')
                if proc.poll() is not None:
                    raise RuntimeError(f'vLLM container exited code={proc.returncode}; inspect server.log')
                free=free_gib(data_dir)
                w.writerow({'timestamp_utc':utc(),'free_gib':free,'elapsed_s':time.monotonic()-started})
                if free<settings['min_storage_free_gib']:
                    raise RuntimeError('Disk nearly full while downloading model')
                try:
                    import urllib.request
                    with urllib.request.urlopen(url+'/health',timeout=2) as r:
                        if r.status==200:
                            break
                except Exception:
                    pass
                time.sleep(3)
            else:
                raise RuntimeError('Server readiness timed out')
        finally:
            f.close()
        with __import__('urllib.request',fromlist=['urlopen']).urlopen(url+'/v1/models',timeout=6) as res:
            atomic(output/'served_models.json',json.load(res))
        # The 90 s comparison window is kept identical to the Xeon study.
        result['measurements']=asyncio.run(measure(url,item['model'],output,
             prompt_tokens=item['prompt_tokens'],output_tokens=item['output_tokens'],
             concurrency=item['concurrency'],duration_s=settings['duration_s'],
             drain_s=settings['drain_s'],request_timeout_s=settings['request_timeout_s'],
             warmup_requests=settings['warmup_requests'],
             warmup_output_tokens=settings['warmup_output_tokens'],
             metrics_interval_s=settings['metrics_interval_s'],should_stop=stopped))
        result['status']='done'
    except (KeyboardInterrupt,InterruptedError):
        result.update(status='interrupted',error='Stopped by user')
    except BaseException as exc:
        result.update(status='timeout' if isinstance(exc,Deadline) else 'failed',
                      error=str(exc),traceback=traceback.format_exc())
        print(f'FAILED {item["model"]} {item["config_id"]}: {exc}',flush=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        if proc:
            try:
                cleanup(name)
            except Exception as exc:
                result['cleanup_error']=str(exc)
            try:
                proc.wait(timeout=7)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        meter_stop.set()
        if meter:
            meter.join(timeout=8)
        if stdout:
            stdout.close()
        result.update(finished_at=utc(),elapsed_s=round(time.monotonic()-started,3))
        atomic(output/'summary.json',result)
        (STATE/'active.json').unlink(missing_ok=True)
    return result


def main():
    for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGALRM):
        signal.signal(sig,handler)
    plan=load(STATE/'plan.json')
    setup=load(STATE/'setup.json')
    if not plan or not setup:
        raise RuntimeError('Run ./setup.sh and ./experiment.sh start first')
    data_dir=Path(setup['data_dir'])
    if not data_dir.is_dir() or data_dir.resolve()!=Path('/data2/alan/ascend910b3-vllm-bench-data').resolve():
        raise RuntimeError('Data directory is missing or no longer mounted at /data2/alan')
    progress=load(STATE/'progress.json',{'plan_id':plan['plan_id'],'runs':{}})
    if progress['plan_id']!=plan['plan_id']:
        raise RuntimeError('Saved plan/progress mismatch')
    # Seed from prior failures so resume does not re-pull known-unsupported models.
    unsupported={}
    for key,prior in progress['runs'].items():
        if prior.get('status')!='failed':
            continue
        msg=unsupported_npu_error(prior)
        if msg:
            unsupported[prior.get('run',{}).get('model') or key.split('|',1)[0]]={
                'message':msg,'output':prior.get('output')}
    for idx,item in enumerate(plan['runs']):
        if stopped():
            break
        key=item['model']+'|'+item['config_id']
        if progress['runs'].get(key,{}).get('status')=='done':
            continue
        print(f'[{utc()}] RUN {idx+1}/{len(plan["runs"])} {key}',flush=True)
        try:
            if item['model'] in unsupported:
                info=unsupported[item['model']]
                print(f'FAIL-FAST unsupported on NPU: {item["model"]}',flush=True)
                result=record_unsupported(item,info['message'],info.get('output'))
            else:
                result=run_one(idx,item,plan,setup)
                msg=unsupported_npu_error(result) if result.get('status')=='failed' else None
                if msg:
                    unsupported[item['model']]={'message':msg,'output':result.get('output')}
        except BaseException as exc:
            result={'run':item,'status':'failed','error':str(exc),'traceback':traceback.format_exc()}
        progress['runs'][key]=result
        atomic(STATE/'progress.json',progress)
        if result['status']=='interrupted':
            break
    (STATE/'controller.json').unlink(missing_ok=True)
    print(f'[{utc()}] Benchmark controller ended',flush=True)


if __name__=='__main__':
    try:
        main()
    except BaseException:
        traceback.print_exc()
        sys.exit(1)
