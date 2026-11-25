"""Ascend-specific container creation, without granting access to unreserved NPUs."""
from __future__ import annotations
import os
from pathlib import Path
import shlex


def docker_command(cfg, item, output, data_dir, container_name):
    devices=item['devices']
    assert devices==list(range(item['tp'])) and set(devices)<=set((0,1,2,3))
    cache=Path(data_dir)/'cache'
    # --privileged is required on Ascend 26.x hosts for ascend_hal / torch.npu;
    # device list + ASCEND_RT_VISIBLE_DEVICES still restrict which NPUs are used.
    cmd=['docker','run','--rm','--privileged','--name',container_name,'--network','host',
         '--ipc','host','--shm-size','8g',
         '--device','/dev/davinci_manager','--device','/dev/devmm_svm',
         '--device','/dev/hisi_hdc']
    for device in devices:
        cmd+=['--device',f'/dev/davinci{device}']
    # Runtime mounts documented by vLLM Ascend for A2-series devices.
    mounts=[('/usr/local/dcmi','/usr/local/dcmi'),
            ('/usr/local/bin/npu-smi','/usr/local/bin/npu-smi'),
            ('/usr/local/Ascend/driver/lib64','/usr/local/Ascend/driver/lib64'),
            ('/usr/local/Ascend/driver/version.info','/usr/local/Ascend/driver/version.info'),
            ('/etc/ascend_install.info','/etc/ascend_install.info')]
    for host,target in mounts:
        if Path(host).exists():
            cmd+=['-v',f'{host}:{target}:ro']
    # All writable caches and process temp space live within /data2/alan.
    for path,target in [('root','/root/.cache'),('huggingface','/root/.cache/huggingface'),
                        ('torch','/cache/torch'),('vllm','/cache/vllm'),
                        ('tmp','/cache/tmp'),('xdg','/cache/xdg')]:
        cmd+=['-v',f'{cache/path}:{target}']
    env={'HF_HOME':'/root/.cache/huggingface',
         'HF_HUB_CACHE':'/root/.cache/huggingface/hub',
         'HUGGINGFACE_HUB_CACHE':'/root/.cache/huggingface/hub',
         'TORCH_HOME':'/cache/torch', 'VLLM_CACHE_ROOT':'/cache/vllm',
         'XDG_CACHE_HOME':'/cache/xdg','TMPDIR':'/cache/tmp',
         # Visible devices are contiguous to avoid confusing rank/device mapping.
         'ASCEND_RT_VISIBLE_DEVICES':','.join(map(str,devices)),
         'PYTORCH_NPU_ALLOC_CONF':'expandable_segments:True',
         'HCCL_CONNECT_TIMEOUT':'1800',
         'VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS':'3000'}
    for key,value in env.items():
        cmd+=['-e',f'{key}={value}']
    # Pass token names only (values come from the runner subprocess env, never argv/logs).
    # Always request them: docker_command is built before the runner injects HF_TOKEN.
    cmd+=['-e','HF_TOKEN','-e','HUGGING_FACE_HUB_TOKEN']
    # Quantized checkpoints keep their native dtype; forcing bf16 breaks AWQ/FP8/W8A8.
    model_l=item['model'].lower()
    quantized=any(x in model_l for x in ('-awq','awq-int4','w8a8','-fp8','gpt-oss','quantized'))
    dtype='auto' if quantized else cfg['dtype']
    argv=['--host','127.0.0.1','--port',str(cfg['host_port']),
          '--dtype',dtype,'--tensor-parallel-size',str(item['tp']),
          '--max-model-len',str(cfg['max_model_len']),
          '--max-num-seqs',str(cfg['max_num_seqs']),
          '--max-num-batched-tokens',str(cfg['max_num_batched_tokens']),
          '--gpu-memory-utilization',str(cfg['gpu_memory_utilization']),
          '--served-model-name',item['model']]
    if not cfg.get('enable_prefix_caching',False):
        argv+=['--no-enable-prefix-caching']
    argv+=cfg.get('extra_vllm_args',[])
    cmd += ['--entrypoint','/bin/bash',cfg['image'],'-lc',
            'exec '+shlex.join(['vllm','serve',item['model']]+argv)]
    return cmd
