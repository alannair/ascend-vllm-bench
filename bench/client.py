"""Closed-loop streaming benchmark; match the CPU runner's client TTFT/TPOT definitions."""
from __future__ import annotations
import asyncio
import json
import statistics
import time
from pathlib import Path
import aiohttp
from .common import csv_open, utc

REQUEST_COLS = ['request_id','client','start_utc','end_utc','ttft_s','mean_tpot_s','latency_s',
                'output_tokens','expected_tokens','prompt_tokens','complete','finish_reason',
                'http_status','error','tokens_within_window','usage_completion_tokens']
TOKEN_COLS = ['request_id','client','token_index','token_id','timestamp_utc','receive_ns_monotonic',
              'time_since_request_s','chunk_index','tokens_in_chunk','index_in_chunk']
METRIC_COLS = ['timestamp_utc','name','labels','value']
SCHED_COLS = ['timestamp_utc','num_requests_running','num_requests_waiting',
              'num_requests_swapped','kv_cache_usage_perc','generation_tokens_total',
              'prompt_tokens_total','scrape_error']


def quantile(xs, p):
    if not xs:
        return None
    values = sorted(xs)
    n = (len(values) - 1) * p
    low = int(n)
    return values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (n - low)


def parse_metrics(body):
    import re
    regex = re.compile(r'^([^\s{]+)(\{.*?\})?\s+([-+\d.eE]+)(?:\s+.*)?$')
    for row in body.splitlines():
        match = regex.match(row)
        if match:
            try:
                yield match.group(1), match.group(2) or '', float(match.group(3))
            except ValueError:
                pass


async def prompt_ids(session, url, model, n):
    base = ('The measured experiment examines numerical reasoning and server performance '
            'in controlled conditions. Continue this neutral laboratory note with details. ')
    # Long prompts should not require a 4K token server prefill merely to tokenize.
    async with session.post(url + '/tokenize', json={
        'model': model, 'prompt': base * (n // 12 + 8)}) as response:
        body = await response.text()
        if response.status != 200:
            raise RuntimeError(f'/tokenize failed: {response.status} {body[:400]}')
    tokens = json.loads(body)
    ids = tokens.get('tokens', tokens.get('token_ids'))
    if not isinstance(ids, list) or len(ids) < n or any(not isinstance(x, int) for x in ids[:n]):
        raise RuntimeError(f'/tokenize did not provide >= {n} token IDs')
    return ids[:n]


async def stream(session, url, model, ids, count, request_id, client, rw, tw,
                 *, deadline_ns=None, timeout_s=420, warmup=False):
    start = time.perf_counter_ns()
    start_wall = utc()
    received = 0
    in_window = 0
    chunks = 0
    timestamps = []
    error = ''
    http_status = 0
    finish = ''
    done = False
    usage = None
    payload = {'model':model, 'prompt':ids, 'min_tokens':count, 'max_tokens':count,
               'ignore_eos':True, 'temperature':0, 'seed':42,
               'stream':True, 'return_token_ids':True,
               'stream_options':{'include_usage':True}}
    try:
        async with session.post(url + '/v1/completions', json=payload,
                                timeout=aiohttp.ClientTimeout(total=timeout_s)) as response:
            http_status = response.status
            if http_status != 200:
                raise RuntimeError(f'HTTP {http_status}: {(await response.text())[:500]}')
            async for line in response.content:
                if not line.startswith(b'data:'):
                    continue
                at = time.perf_counter_ns()
                raw = line[5:].strip()
                if raw == b'[DONE]':
                    done = True
                    break
                try:
                    obj = json.loads(raw)
                except (ValueError, UnicodeDecodeError) as exc:
                    raise RuntimeError(f'Invalid SSE event: {raw[:120]!r}') from exc
                if isinstance(obj.get('usage'), dict):
                    usage = obj['usage'].get('completion_tokens')
                for choice in obj.get('choices', []):
                    if choice.get('index', 0) != 0:
                        continue
                    if choice.get('finish_reason') is not None:
                        finish = choice['finish_reason']
                    new = choice.get('token_ids')
                    if new is None:
                        if choice.get('text'):
                            raise RuntimeError('Missing return_token_ids in streaming response; check vLLM Ascend image')
                        continue
                    if not isinstance(new, list):
                        raise RuntimeError('Invalid token_ids in stream')
                    if not new:
                        continue
                    chunks += 1
                    if deadline_ns is None or at <= deadline_ns:
                        in_window += len(new)
                    for j, token_id in enumerate(new):
                        received += 1
                        timestamps.append(at)
                        if not warmup:
                            tw.writerow({'request_id':request_id,'client':client,'token_index':received,
                                         'token_id':token_id,'timestamp_utc':utc(),
                                         'receive_ns_monotonic':at,
                                         'time_since_request_s':(at-start)/1e9,
                                         'chunk_index':chunks,'tokens_in_chunk':len(new),'index_in_chunk':j})
    except asyncio.CancelledError:
        error = 'cancelled_at_window_end'
        raise
    except Exception as exc:
        error = str(exc)
    finally:
        end = time.perf_counter_ns()
        row = {'request_id':request_id,'client':client,'start_utc':start_wall,'end_utc':utc(),
               'ttft_s':(timestamps[0]-start)/1e9 if timestamps else None,
               'mean_tpot_s':(timestamps[-1]-timestamps[0])/1e9/(len(timestamps)-1) if len(timestamps)>1 else None,
               'latency_s':(end-start)/1e9,'output_tokens':received,'expected_tokens':count,
               'prompt_tokens':len(ids),'complete':int(done and not error and received==count),
               'finish_reason':finish,'http_status':http_status,'error':error,
               'tokens_within_window':in_window,'usage_completion_tokens':usage}
        if not warmup:
            rw.writerow(row)
    return row


async def metrics(session, url, output, done, interval):
    all_f, all_w = csv_open(output/'metrics_long.csv', METRIC_COLS)
    selected_f, selected_w = csv_open(output/'metrics.csv', SCHED_COLS)
    mapping = {'num_requests_running':'vllm:num_requests_running',
               'num_requests_waiting':'vllm:num_requests_waiting',
               'num_requests_swapped':'vllm:num_requests_swapped',
               'kv_cache_usage_perc':'vllm:kv_cache_usage_perc',
               'generation_tokens_total':'vllm:generation_tokens_total',
               'prompt_tokens_total':'vllm:prompt_tokens_total'}
    try:
        while not done.is_set():
            ts = utc()
            sample = {'timestamp_utc':ts}
            try:
                async with session.get(url+'/metrics', timeout=aiohttp.ClientTimeout(total=4)) as res:
                    if res.status != 200:
                        raise RuntimeError(f'HTTP {res.status}')
                    body = await res.text()
                sums = {}
                for name, labels, value in parse_metrics(body):
                    if name.startswith('vllm:'):
                        all_w.writerow({'timestamp_utc':ts,'name':name,'labels':labels,'value':value})
                        sums[name] = sums.get(name,0) + value
                sample.update({field:sums.get(metric,'') for field,metric in mapping.items()})
            except Exception as exc:
                sample['scrape_error'] = str(exc)
            selected_w.writerow(sample)
            try:
                await asyncio.wait_for(done.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass
    finally:
        all_f.close()
        selected_f.close()


async def measure(url, model, output, *, prompt_tokens, output_tokens, concurrency,
                  duration_s, drain_s, request_timeout_s, warmup_requests,
                  warmup_output_tokens, metrics_interval_s, should_stop):
    output = Path(output)
    request_f, request_w = csv_open(output/'requests.csv', REQUEST_COLS)
    token_f, token_w = csv_open(output/'token_events.csv', TOKEN_COLS)
    phase_f, phase_w = csv_open(output/'phases.csv', ['timestamp_utc','monotonic_ns','phase'])
    def phase(p):
        phase_w.writerow({'timestamp_utc':utc(),'monotonic_ns':time.perf_counter_ns(),'phase':p})
    rows = []
    failures = []
    started = 0
    done = asyncio.Event()
    connector = aiohttp.TCPConnector(limit=concurrency+16)
    async with aiohttp.ClientSession(connector=connector,timeout=aiohttp.ClientTimeout(total=None)) as session:
        try:
            ids = await prompt_ids(session, url, model, prompt_tokens)
            (output/'prompt_token_ids.json').write_text(json.dumps(ids))
            phase('warmup_start')
            for i in range(warmup_requests):
                r = await stream(session,url,model,ids,warmup_output_tokens,f'warmup-{i}',i,
                                 request_w,token_w,warmup=True,timeout_s=60)
                if not r['complete']:
                    raise RuntimeError('Warmup failed: '+r['error'])
            phase('warmup_end')
            polling = asyncio.create_task(metrics(session,url,output,done,metrics_interval_s))
            phase('measurement_start')
            started_at = time.perf_counter_ns()
            deadline = started_at + int(duration_s*1e9)
            async def worker(client):
                nonlocal started
                while time.perf_counter_ns() < deadline and not should_stop():
                    started += 1
                    prompt = ids.copy()
                    if len(prompt) >= 4:
                        prompt[-1] = ids[-1-(started%3)]
                    r = await stream(session,url,model,prompt,output_tokens,
                                     f'c{client:03d}-r{started:07d}',client,
                                     request_w,token_w,deadline_ns=deadline,
                                     timeout_s=request_timeout_s)
                    rows.append(r)
                    if r['error']:
                        failures.append(r['error'])
                        if len(failures) >= 3:
                            return
            tasks = [asyncio.create_task(worker(c)) for c in range(concurrency)]
            try:
                while time.perf_counter_ns() < deadline and not should_stop():
                    await asyncio.sleep(.2)
                phase('measurement_window_end')
                remaining = max(0,(deadline + int(drain_s*1e9)-time.perf_counter_ns())/1e9)
                _, pending = await asyncio.wait(tasks,timeout=remaining)
                for task in pending:
                    task.cancel()
                await asyncio.gather(*tasks,return_exceptions=True)
            finally:
                phase('drain_end')
                done.set()
                await polling
            if should_stop():
                raise InterruptedError('Experiment interrupted')
            if failures and not any(r['output_tokens'] for r in rows):
                raise RuntimeError('All requests failed: '+failures[0])
        finally:
            request_f.close()
            token_f.close()
            phase_f.close()
    completed = [r for r in rows if r['complete']]
    ttft = [r['ttft_s'] for r in completed if r['ttft_s'] is not None]
    tpot = [r['mean_tpot_s'] for r in completed if r['mean_tpot_s'] is not None]
    all_ttft = [r['ttft_s'] for r in rows if r['ttft_s'] is not None]
    all_tpot = [r['mean_tpot_s'] for r in rows if r['mean_tpot_s'] is not None]
    return {'started_requests':started,'completed_requests':len(completed),
            'observed_requests':len(rows), 'errors':failures[:15],
            'observed_output_tokens_in_window':sum(r['tokens_within_window'] for r in rows),
            'measurement_window_s':duration_s,
            'delivered_tokens_per_s':sum(r['tokens_within_window'] for r in rows)/duration_s,
            'ttft_median_s':quantile(ttft,.5),'ttft_p90_s':quantile(ttft,.9),
            'ttft_observed_median_s':quantile(all_ttft,.5),
            'mean_tpot_median_s':quantile(tpot,.5),'mean_tpot_p90_s':quantile(tpot,.9),
            'mean_tpot_observed_median_s':quantile(all_tpot,.5),
            'client_tpot_definition':'(last-first token timestamp)/(N-1)',
            'warning':'When streaming groups multiple tokens in one SSE event, they share one timestamp'}
