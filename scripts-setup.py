#!/usr/bin/env python3
"""Host preflight: NEVER rewrite system Docker config or install CANN into the host."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import venv

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from bench.common import STATE, LOGS, GIB, atomic, utc
from bench.hardware import npu_info, npu_memory_mb
from bench.plan import config

DATA=Path('/data2/alan/ascend910b3-vllm-bench-data')
TOKEN=Path('/data2/alan/.hf_token')


def run(args,timeout=30,**kw):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          text=True,timeout=timeout,**kw)


def install_host_commands():
    commands={'docker':'docker','npu-smi':None,'numactl':'numactl'}
    missing=[x for x in commands if not shutil.which(x)]
    if 'npu-smi' in missing:
        raise RuntimeError('npu-smi missing: install the matching Huawei Ascend host driver first')
    if not missing:
        return
    if shutil.which('apt-get'):
        manager=['apt-get','install','-y']
        packages=['docker.io' if x=='docker' else 'numactl' for x in missing]
    elif shutil.which('dnf') or shutil.which('yum'):
        manager=[shutil.which('dnf') or shutil.which('yum'),'install','-y']
        packages=['docker' if x=='docker' else 'numactl' for x in missing]
    else:
        raise RuntimeError('Missing host packages '+str(missing)+'; install manually')
    prefix=[] if os.geteuid()==0 else ['sudo','-n']
    print('Installing missing packages:',packages,flush=True)
    subprocess.run(prefix+manager+packages,check=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--no-pull',action='store_true')
    args=p.parse_args()
    if platform.system()!='Linux' or platform.machine() not in ('aarch64','arm64'):
        raise RuntimeError('This benchmark requires Linux aarch64 host')
    if sys.version_info<(3,10):
        raise RuntimeError('Python >=3.10 required on the ARM host')
    if not str(ROOT.resolve()).startswith('/data2/alan/'):
        raise RuntimeError('Clone/move repository under /data2/alan before running setup')
    if not TOKEN.is_file():
        raise RuntimeError('Hugging Face token missing at /data2/alan/.hf_token')
    if not TOKEN.read_text().strip():
        raise RuntimeError('HF token file is empty')
    DATA.mkdir(parents=True,exist_ok=True)
    for sub in ('cache/root','cache/huggingface','cache/torch','cache/vllm','cache/tmp','cache/xdg','logs'):
        (DATA/sub).mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(DATA).free < 100*GIB:
        raise RuntimeError('/data2/alan needs at least 100 GiB free for all 47 model downloads')
    if LOGS.is_symlink():
        if LOGS.resolve()!=(DATA/'logs').resolve():
            raise RuntimeError('logs symlink points away from /data2/alan: move it before setup')
    elif LOGS.exists():
        if not LOGS.is_dir() or any(LOGS.iterdir()):
            raise RuntimeError('Existing logs directory not empty; move it to '+str(DATA/'logs'))
        LOGS.rmdir()
        LOGS.symlink_to(DATA/'logs',target_is_directory=True)
    else:
        LOGS.symlink_to(DATA/'logs',target_is_directory=True)
    install_host_commands()
    cfg=config()
    devices=cfg['devices']
    if devices!=[0,1,2,3]:
        raise RuntimeError('Only NPU devices 0-3 are reserved for this study')
    all_info=npu_info()
    print('Host npu-smi info:\n',all_info[:7000],flush=True)
    hardware={}
    for device in devices:
        path=Path(f'/dev/davinci{device}')
        if not path.exists():
            raise RuntimeError(f'Reserved {path} does not exist')
        raw=npu_info(device)
        mem=npu_memory_mb(raw)
        hardware[str(device)]={'info':raw,'memory_mb':mem}
        if mem is not None and mem[1]<59000:
            raise RuntimeError(f'NPU {device} shows only {mem[1]} MB; expected 64 GiB')
        print(f'NPU {device} memory:',mem or 'unknown format; raw preserved')
    numa=run(['numactl','--hardware'])
    if numa.returncode:
        raise RuntimeError('Cannot inspect host NUMA topology: '+numa.stderr[-500:])
    print('NUMA hardware topology:\n',numa.stdout[:4000],flush=True)
    docker=run(['docker','info','--format','{{.DockerRootDir}}'])
    if docker.returncode:
        raise RuntimeError('Docker daemon not usable by this user: '+docker.stderr[-500:])
    docker_root=Path(docker.stdout.strip())
    if not str(docker_root).startswith('/data2/alan'):
        print('WARNING: Docker image layers live at',docker_root,
              'outside /data2/alan. Host daemon storage is managed separately.',flush=True)
    image=os.environ.get('ASCEND_IMAGE') or cfg['image']
    if image!=cfg['image']:
        raise RuntimeError('To use ASCEND_IMAGE, set configs/default.json image to the same tag')
    if not args.no_pull:
        print('Pulling',image,flush=True)
        subprocess.run(['docker','pull',image],check=True)
    ident=run(['docker','image','inspect','--format','{{.Id}}',image])
    if ident.returncode:
        raise RuntimeError('Ascend image missing: '+image)
    # Verify image import and device visibility with only the reserved NPU 0.
    # Ascend 26.x on this host needs --privileged for ascend_hal (torch.npu);
    # ASCEND_RT_VISIBLE_DEVICES keeps the probe on card 0 despite privileged /dev.
    probe=['docker','run','--rm','--privileged',
           '--device','/dev/davinci0',
           '--device','/dev/davinci_manager','--device','/dev/devmm_svm',
           '--device','/dev/hisi_hdc',
           '-e','ASCEND_RT_VISIBLE_DEVICES=0']
    for host in ['/usr/local/dcmi','/usr/local/bin/npu-smi','/usr/local/Ascend/driver/lib64',
                 '/usr/local/Ascend/driver/version.info','/etc/ascend_install.info']:
        if Path(host).exists():
            probe+=['-v',f'{host}:{host}:ro']
    code=('import torch,torch_npu,vllm,vllm_ascend; '
          'assert torch.npu.is_available(); print("ASCEND_PROBE_OK",torch.npu.device_count())')
    probe+=['--entrypoint','python3',image,'-c',code]
    status=run(probe,timeout=180)
    if status.returncode or 'ASCEND_PROBE_OK' not in status.stdout:
        raise RuntimeError('Container/CANN/torch_npu verification failed:\n'+status.stderr[-2500:]+status.stdout[-1000:])
    print('Ascend container probe:',status.stdout.strip())
    env=ROOT/'.venv'
    py=env/'bin/python'
    if not py.is_file():
        venv.create(env,with_pip=True)
    # uv-created venvs often omit pip; bootstrap it before requirements install.
    pip_ok=run([str(py),'-m','pip','--version']).returncode==0
    if not pip_ok:
        subprocess.run([str(py),'-m','ensurepip','--upgrade'],check=True)
    subprocess.run([str(py),'-m','pip','install','--disable-pip-version-check',
                    '-r',str(ROOT/'requirements.txt')],check=True)
    inv={'setup_utc':utc(),'image':image,'image_id':ident.stdout.strip(),
         'data_dir':str(DATA),'docker_root':str(docker_root),'hardware':hardware,
         'npu_smi_full_info':all_info,'numactl_hardware':numa.stdout,
         'host':platform.uname()._asdict()}
    atomic(STATE/'setup.json',inv)
    print('\nREADY: ./experiment.sh start')
    print('Data:',DATA,'Code:',ROOT,'Logs:',LOGS)


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('SETUP FAILED:',exc,file=sys.stderr)
        sys.exit(1)
