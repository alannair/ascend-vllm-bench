"""Exact CPU-report model IDs, and 8 decode + 12 prefill runs per model."""
from __future__ import annotations
import fnmatch
import json
from .common import ROOT, slug, fingerprint


def config():
    cfg=json.loads((ROOT/'configs/default.json').read_text())
    cfg['models']=json.loads((ROOT/'configs/models.json').read_text())
    return cfg


def tp_for(model, cfg):
    """Conservative *initial* TP choice from parameter count; not a fit guarantee.

    A checkpoint may use MoE, quantization, tied embeddings, unusual tensor sizes,
    unsupported quantization or non-divisible attention heads. Runtime verifies it.
    """
    if model in cfg.get('tp_overrides',{}):
        chosen=int(cfg['tp_overrides'][model])
    else:
        import re
        m=re.search(r'(?i)(\d+(?:\.\d+)?)b(?:-|$)',model)
        billion=float(m.group(1)) if m else 8
        # BF16 ~= 2GB / billion weights; reserve room for activations/KV.
        # 32B BF16 exceeds the comfortable per-64GB-device working set.
        quantized = any(x in model.lower() for x in ('-awq','awq-int4','w8a8','-fp8','gpt-oss'))
        # CPU-intended W8A8/AWQ/FP8 checkpoints usually fit on one 64 GiB NPU;
        # compatibility is *not* assumed and unsupported kernels are reported.
        chosen=2 if billion>=24 and not quantized else 1
    if chosen not in (1,2,4):
        raise ValueError(f'TP for {model} must be 1, 2 or 4')
    return chosen


def make_plan(cfg, model_filter=None, studies=None, max_runs=None):
    selected=[m for m in cfg['models'] if not model_filter or any(
        fnmatch.fnmatchcase(m,p) if any(c in p for c in '*?[') else m==p
        for p in model_filter)]
    if not selected:
        raise ValueError('No model matches --models')
    studies=studies or ['decode','prefill']
    if set(studies)-{'decode','prefill'}:
        raise ValueError('Invalid study type')
    devices=cfg['devices']
    if devices!=[0,1,2,3]:
        raise ValueError('Reserved device policy requires exactly NPUs 0,1,2,3')
    entries=[]
    for model in selected:
        tp=tp_for(model,cfg)
        for study in studies:
            sweep=cfg['sweeps'][study]
            for input_tokens in sweep['prompt_tokens']:
                for output_tokens in sweep['output_tokens']:
                    for concurrency in sweep['concurrency']:
                        name=(f'{study}_tp{tp}_in{input_tokens:04d}_out{output_tokens:04d}'
                              f'_clients{concurrency:03d}')
                        entries.append({'model':model,'model_slug':slug(model),'study':study,
                                        'config_id':name,'tp':tp,'devices':devices[:tp],
                                        'prompt_tokens':input_tokens,'output_tokens':output_tokens,
                                        'concurrency':concurrency})
    if max_runs is not None:
        if max_runs<1:
            raise ValueError('--max-runs must be positive')
        entries=entries[:max_runs]
    item={'config':cfg,'models':selected,'studies':studies,'runs':entries}
    item['plan_id']=fingerprint(item)
    return item
