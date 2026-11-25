"""Ascend device inspection; never infer the host device IDs from 0-based worker IDs."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path
from .common import utc, csv_open


def _run_smi(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=15)
    if p.returncode:
        raise RuntimeError(f"{' '.join(cmd)} failed: {p.stderr[:400]} {p.stdout[:400]}")
    return p.stdout


def _extract_device_section(raw, device):
    """Pull the overview-table row pair for one NPU id (name row + chip/HBM row)."""
    device = int(device)
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells:
            continue
        toks = cells[0].split()
        # Name row looks like "0     910B3"; the following chip row is just "0".
        if len(toks) >= 2 and toks[0] == str(device):
            chunk = [line]
            if i + 1 < len(lines):
                chunk.append(lines[i + 1])
            return '\n'.join(chunk)
    return None


def npu_info(device=None):
    """Return npu-smi inventory text.

    Ascend 26.x drivers reject `npu-smi info -t common` without `-i`, and the
    typed `common` view only reports usage rates. Plain `npu-smi info` works
    without a card id and includes absolute HBM used/total MB.
    """
    overview = _run_smi(['npu-smi', 'info'])
    if device is None:
        return overview
    section = _extract_device_section(overview, device) or ''
    typed = _run_smi(['npu-smi', 'info', '-t', 'common', '-i', str(device)])
    if section:
        return f'{section}\n{typed}'
    return typed


def npu_memory_mb(raw):
    """Read common npu-smi 'Memory-Usage(MB)' / 'used / total' lines.

    If the installed npu-smi format differs, preserve raw output and return None.
    """
    patterns = [r'Memory-Usage\(MB\)\s*\|\s*(\d+)\s*/\s*(\d+)',
                r'HBM-Usage\(MB\)\s*\|\s*(\d+)\s*/\s*(\d+)',
                r'(\d+)\s*/\s*(\d+)\s*\|[^\n]*?Memory-Usage',
                r'(\d+)\s*/\s*(\d+)\s*\|[^\n]*?HBM-Usage',
                r'Memory Usage\s*:\s*(\d+)\s*/\s*(\d+)',
                r'HBM Usage\s*:\s*(\d+)\s*/\s*(\d+)']
    for regex in patterns:
        found = re.search(regex, raw, re.I)
        if found:
            return int(found.group(1)), int(found.group(2))
    # Typical Huawei full-table row: '... | 20 | 20 | 0 / 65536 | ...'
    # Prefer the rightmost used/total on the chip row (HBM), not DDR 0/0.
    found = re.search(r'(?<!\d)(\d+)\s*/\s*(65536|65535|65534)(?!\d)', raw)
    if found:
        return int(found.group(1)), int(found.group(2))
    # Typed `usages` view: capacity + percent (approximate absolute MB).
    cap = re.search(r'HBM Capacity\(MB\)\s*:\s*(\d+)', raw, re.I)
    rate = re.search(r'HBM Usage Rate\(%\)\s*:\s*(\d+)', raw, re.I)
    if cap and rate and int(cap.group(1)) > 0:
        total = int(cap.group(1))
        return int(round(total * int(rate.group(1)) / 100.0)), total
    return None


def sample_npus(devices, output, interval, stop):
    """Host-side collection; output persists even if npu-smi parsing fails."""
    import time
    output = Path(output)
    raw_f = (output/'npu_smi_raw.log').open('a', buffering=1)
    f, w = csv_open(output/'npu_memory.csv',
                    ['timestamp_utc', 'device', 'memory_used_mb', 'memory_total_mb', 'npu_smi_error'])
    try:
        while not stop.is_set():
            start = time.monotonic()
            at = utc()
            overview_error = None
            overview = ''
            try:
                overview = _run_smi(['npu-smi', 'info'])
            except Exception as exc:
                overview_error = str(exc)
            for device in devices:
                try:
                    if overview_error:
                        raise RuntimeError(overview_error)
                    section = _extract_device_section(overview, device) or ''
                    print(f'==== {at} NPU {device} ====', file=raw_f)
                    print(section or overview, file=raw_f)
                    mem = npu_memory_mb(section) if section else npu_memory_mb(overview)
                    w.writerow({'timestamp_utc': at, 'device': device,
                                'memory_used_mb': mem[0] if mem else '',
                                'memory_total_mb': mem[1] if mem else '',
                                'npu_smi_error': '' if mem else 'unparsed; see npu_smi_raw.log'})
                except Exception as exc:
                    w.writerow({'timestamp_utc': at, 'device': device, 'npu_smi_error': str(exc)})
            stop.wait(max(0.1, interval - (time.monotonic() - start)))
    finally:
        f.close()
        raw_f.close()
