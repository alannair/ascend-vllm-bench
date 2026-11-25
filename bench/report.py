"""Aggregate vLLM server-side ITL from Prometheus histogram counter differences."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path


def server_itl_mean_ms(attempt_dir: Path):
    """Delta histogram sum / delta count over recorded measurement samples.

    This is approximate because scrape timestamps are 1s apart, and not
    exactly aligned with the measurement phase boundaries.
    """
    path=Path(attempt_dir)/'metrics_long.csv'
    if not path.exists():
        return None
    series=defaultdict(lambda:defaultdict(float))
    with path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            metric=row['name']
            if metric in ('vllm:inter_token_latency_seconds_sum',
                          'vllm:inter_token_latency_seconds_count'):
                try:
                    series[row['timestamp_utc']][metric]+=float(row['value'])
                except (ValueError,KeyError):
                    pass
    if len(series)<2:
        return None
    keys=sorted(series)
    first,last=series[keys[0]],series[keys[-1]]
    delta_n=last.get('vllm:inter_token_latency_seconds_count',0)-first.get(
        'vllm:inter_token_latency_seconds_count',0)
    delta_s=last.get('vllm:inter_token_latency_seconds_sum',0)-first.get(
        'vllm:inter_token_latency_seconds_sum',0)
    return delta_s/delta_n*1000 if delta_n>0 and delta_s>=0 else None
