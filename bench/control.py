"""Start/stop/resume/plan/status/report; no run state is overwritten on resume."""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from collections import Counter
from .common import ROOT, STATE, LOGS, atomic, load, stamp, utc
from .plan import config, make_plan
from .report import server_itl_mean_ms


def running_pid():
    p=load(STATE/'controller.json',{})
    pid=p.get('pid')
    if not pid:
        return None
    try:
        if b'bench.runner' in Path(f'/proc/{pid}/cmdline').read_bytes():
            return int(pid)
    except OSError:
        pass
    return None


def start_controller(plan, foreground=False):
    if running_pid():
        raise RuntimeError(f'Controller already running: {running_pid()}')
    (STATE/'stop.flag').unlink(missing_ok=True)
    log=LOGS/('controller-'+stamp()+'.log')
    cmd=[str(ROOT/'.venv/bin/python'),'-m','bench.runner']
    if foreground:
        proc=subprocess.Popen(cmd,cwd=ROOT)
        atomic(STATE/'controller.json',{'pid':proc.pid,'log':'foreground','plan_id':plan['plan_id']})
        try:
            return proc.wait()
        except KeyboardInterrupt:
            stop()
            return 130
    with log.open('w',buffering=1) as stream:
        proc=subprocess.Popen(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    atomic(STATE/'controller.json',{'pid':proc.pid,'log':str(log),'plan_id':plan['plan_id']})
    time.sleep(.25)
    if proc.poll() is not None:
        raise RuntimeError(f'Controller exited with code {proc.returncode}; inspect {log}')
    print('Started PID',proc.pid,'Log:',log)
    print('Monitor: tail -f',log)
    return 0


def stop():
    STATE.mkdir(parents=True,exist_ok=True)
    (STATE/'stop.flag').write_text(utc())
    pid=running_pid()
    if pid:
        os.kill(pid,signal.SIGTERM)
        for _ in range(40):
            if not running_pid():
                break
            time.sleep(.25)
    active=load(STATE/'active.json',{})
    name=active.get('container','')
    if name.startswith('ascend910b3-bench-'):
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=15,check=False)
    if running_pid():
        os.kill(pid,signal.SIGKILL)
    (STATE/'controller.json').unlink(missing_ok=True)
    print('Stopped; ./experiment.sh resume will retry unfinished runs')
    return 0


def status():
    pid=running_pid()
    plan=load(STATE/'plan.json')
    progress=load(STATE/'progress.json',{'runs':{}})
    print('Controller:',f'running PID={pid}' if pid else 'stopped')
    if plan:
        counts=Counter(r['status'] for r in progress['runs'].values())
        print('Plan:',plan['plan_id'],'runs:',len(plan['runs']), 'statuses:',dict(counts))
        print('Remaining:',len(plan['runs'])-counts['done'])
    active=load(STATE/'active.json')
    if active and pid:
        print('Active:',active)
    return 0


def report():
    rows=[]
    for f in LOGS.glob('*/**/attempt-*/summary.json'):
        item=load(f,{})
        run=item.get('run',{})
        measure=item.get('measurements',{})
        rows.append({'model':run.get('model'),'study':run.get('study'),
                     'config_id':run.get('config_id'),'tp':run.get('tp'),
                     'prompt_tokens':run.get('prompt_tokens'),
                     'output_tokens':run.get('output_tokens'),
                     'concurrency':run.get('concurrency'),
                     'status':item.get('status'),'error':item.get('error'),
                     'ttft_median_s':measure.get('ttft_median_s'),
                     'ttft_observed_median_s':measure.get('ttft_observed_median_s'),
                     'mean_tpot_median_s':measure.get('mean_tpot_median_s'),
                     'mean_tpot_observed_median_s':measure.get('mean_tpot_observed_median_s'),
                     'delivered_tokens_per_s':measure.get('delivered_tokens_per_s'),
                     'server_itl_mean_ms_approx':server_itl_mean_ms(f.parent),
                     'completed_requests':measure.get('completed_requests'),
                     'attempt_dir':str(f.parent)})
    cols=['model','study','config_id','tp','prompt_tokens','output_tokens',
          'concurrency','status','error','ttft_median_s','ttft_observed_median_s','mean_tpot_median_s',
          'mean_tpot_observed_median_s','delivered_tokens_per_s',
          'server_itl_mean_ms_approx','completed_requests','attempt_dir']
    LOGS.mkdir(parents=True,exist_ok=True)
    with (LOGS/'results.csv').open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(rows,key=lambda x:(x['model'] or '',x['config_id'] or '',x['attempt_dir'])))
    print('Wrote',LOGS/'results.csv','with',len(rows),'attempts')
    return 0


def main():
    parser=argparse.ArgumentParser(prog='./experiment.sh')
    sub=parser.add_subparsers(dest='action',required=True)
    for action in ('start','plan'):
        p=sub.add_parser(action)
        p.add_argument('--models',help='Comma-separated globs/substrings')
        p.add_argument('--studies',default='decode,prefill',help='decode,prefill or either')
        p.add_argument('--max-runs',type=int)
        if action=='start':
            p.add_argument('--foreground',action='store_true')
    sub.add_parser('resume').add_argument('--foreground',action='store_true')
    for action in ('stop','status','report'):
        sub.add_parser(action)
    args=parser.parse_args()
    if args.action=='stop':
        return stop()
    if args.action=='status':
        return status()
    if args.action=='report':
        return report()
    if args.action in ('start','plan'):
        cfg=config()
        models=[x.strip() for x in args.models.split(',')] if args.models else None
        plan=make_plan(cfg,models,args.studies.split(','),args.max_runs)
        print(f'Plan {plan["plan_id"]}: {len(plan["runs"])} runs over {len(plan["models"])} models')
        if args.action=='plan':
            for run in plan['runs']:
                print(run['model'],run['config_id'],'NPUs',run['devices'])
            return 0
        if running_pid():
            raise RuntimeError('Already running; stop before creating a new plan')
        setup=load(STATE/'setup.json')
        if not setup or not (ROOT/'.venv/bin/python').exists():
            raise RuntimeError('Run ./setup.sh first')
        if setup['image']!=cfg['image']:
            raise RuntimeError('Docker image changed since setup; rerun ./setup.sh')
        atomic(STATE/'plan.json',plan)
        atomic(STATE/'progress.json',{'plan_id':plan['plan_id'],'runs':{}})
        return start_controller(plan,args.foreground)
    if args.action=='resume':
        plan=load(STATE/'plan.json')
        if not plan:
            raise RuntimeError('No saved plan; use start')
        if not load(STATE/'setup.json'):
            raise RuntimeError('Setup missing')
        return start_controller(plan,args.foreground)
    return 1


if __name__=='__main__':
    try:
        sys.exit(main() or 0)
    except Exception as exc:
        print('ERROR:',exc,file=sys.stderr)
        sys.exit(1)
