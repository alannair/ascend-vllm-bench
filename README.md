# Ascend 910B3 vLLM benchmark: CPU comparison

**Arm64 host, four reserved Ascend 910B3 NPUs (0–3), 64 GiB per NPU.** A repeatable, first-party vLLM-Ascend server benchmark matching the model IDs from `alannair/xeon6-vllm-decode-bench` CPU reports (`REPORT_PINNED.md`, `NO_RECIPE_REPORT.md`).

This repository runs all 47 distinct HF model IDs mentioned in those reports (quantized variants are **separate models**). It does not replace quantized models with BF16 checkpoints without asking. **Some CPU-specific quantization methods or architectures may be unsupported by vLLM-Ascend**. Those attempts will fail with the actual error in `server.log` and `summary.json`; success is never fabricated.

## Quick start on the 910B3 ARM host

Place **the repository itself** under `/data2/alan`, then:

```bash
cd /data2/alan/ascend910b3-vllm-bench
./setup.sh
./experiment.sh plan
./experiment.sh start
# later:
./experiment.sh status
./experiment.sh stop
./experiment.sh resume
./experiment.sh report
```

`/data2/alan/.hf_token` must exist and contain only the raw Hugging Face token. The setup reads it but **never prints or copies it into the repository**. The Docker process receives it as a temporary environment variable (`docker run -e HF_TOKEN` with no token in argv). Use `chmod 600 /data2/alan/.hf_token` to protect it. Gated repos also require that the token's account be granted access.

Docker, the matching Huawei Ascend host driver (`npu-smi`) and the device nodes must work. `setup.sh` can install Docker or `numactl` via apt/dnf/yum if missing and permissions allow; it **cannot** install or repair host kernel drivers, firmware or BIOS settings. It checks all four devices via `npu-smi info -i N`, downloads the pinned official Ascend A2/openEuler Docker image, checks `torch.npu.is_available()` and `vllm_ascend` inside the container, and creates a Python venv. `--no-pull` skips downloading an already-present image. Initial image and host-driver compatibility **must be confirmed on the real machine**; simply importing a library does not prove every model works.

**First run recommendation:**

```bash
./experiment.sh plan --models 'Qwen/Qwen3-4B' --max-runs 2
./experiment.sh start --models 'Qwen/Qwen3-4B' --max-runs 2
# watch the printed controller log; then
./experiment.sh report
```

Only after this passes, run `./experiment.sh start` for the full plan. `start` creates a new plan and resets its progress tracker; it **never deletes** previous per-attempt logs. `resume` reuses the saved plan and skips completed configurations. Failed or interrupted runs are retried in new attempt folders.

## Studies

| Study | Exact prompt tokens | Exact output tokens | Closed-loop clients | Runs/model |
|---|---|---|---|---:|
| Decode | 32 | 512 | 1, 2, 4, 8, 16, 32, 64, 128 | 8 |
| Prefill | 256, 1024, 4096 | 32 | 1, 8, 32, 128 | 12 |

**47 models × 20 configurations = 940 planned runs** (subject to supported model formats and successful server starts). One server runs at a time. Input is an exactly sized **list of model token IDs**, obtained via vLLM's `/tokenize`; no word-count approximation. Outputs request `min_tokens=N`, `max_tokens=N`, and `ignore_eos=true`. Non-completing requests remain in raw logs but do not enter complete-request percentile summaries. The 90-second steady-state measurement window, 8+ second drain, client-side streaming TTFT and mean TPOT definitions track the CPU study. The client also calculates observed-request metrics even when a slow 512-token request cannot complete before the window ends.

### NPU allocation and tensor parallelism

* Default single-NPU inference uses **device 0 only**.
* BF16 models >=24B use **TP=2 on devices 0 and 1** by default; quantized 32B models typically start at TP=1 when expected to fit into 64 GiB.
* Override unusual checkpoint fit or sharding requirements in `configs/default.json` `tp_overrides`, e.g. `"Qwen/Qwen3-32B": 4`. Allowed TP choices are 1, 2 or 4 (always **contiguous device IDs** 0..TP-1). TP=4 uses devices 0–3.
* Setup and the runner **never expose NPUs 4–7** to the Docker container. The collector also samples only the NPUs assigned to that run.
* Parameter-count-based TP choices are estimates, **not proof of fit**. Memory may be consumed by KV blocks, workspace, graph compilation, fragmentation and attention head/sharding restrictions. Review actual NPU allocation and `server.log` before comparing TP configs.

Changes to TP modify the `config_id`, so results never conflate one-NPU runs with multi-NPU runs. For direct CPU-vs-NPU comparisons, retain TP and NPU count in analysis; a TP2 run measures two accelerators, not one.

### Storage and Docker

The repository is intended for `/data2/alan/ascend910b3-vllm-bench`. Its persistent data is under `/data2/alan/ascend910b3-vllm-bench-data/`:

```
cache/huggingface/   # models and tokenizer files
cache/root/          # image /root/.cache miscellaneous libraries
cache/torch/
cache/vllm/
cache/xdg/
cache/tmp/
logs/                # ./logs in repository is a symlink here
```

The setup requires 100 GiB free, with 12 GiB reserved as a safety floor at download time. All study output files, prompts, metrics and raw NPU telemetry live on this partition. **Docker's host-managed image layers may live elsewhere** (`docker info --format '{{.DockerRootDir}}'`); setup warns instead of modifying a shared daemon. If the host Docker root is on a small system disk, arrange a data-root migration to `/data2/alan` with the system administrator before pulling this image. The requirement for all Docker bytes to live there cannot be met by bind mounts alone.

## Instrumentation and outputs

```
logs/<HF owner__model>/<study>_tpN_inXXXX_outXXXX_clientsYYY/attempt-<UTC>/
  config.json                # complete image tag/digest, TP, NPU IDs, exact command
  npu_info_0.txt             # preflight per-device raw info
  npu_smi_raw.log            # every sampled original npu-smi output
  npu_memory.csv             # timestamp, device, used MB, total MB, parsing errors
  server.log                # vLLM-Ascend startup errors and runtime logs
  served_models.json        # /v1/models
  prompt_token_ids.json     # exact prompt ids
  phases.csv                # timestamps of warmup/measurement/drain
  requests.csv              # each client request TTFT, TPOT, completeness, error
  token_events.csv          # each emitted token id and monotonic receive time
  metrics.csv               # running/waiting/queue/KV vLLM snapshots
  metrics_long.csv          # every vllm:* prometheus sample (with labels)
  startup_storage.csv       # free space while loading/downloading model
  summary.json              # status, errors, percentiles, throughput, duration
logs/results.csv            # flattened summaries generated by `report`
```

`npu_memory.csv` is a **best-effort parser** of host `npu-smi info -i`; the raw output is always kept. An unknown firmware/driver output format produces blank numeric fields and a parsing warning, not a false zero. Polling defaults to 1 second. Server-side Prometheus polling also defaults to 1 second. Note that `npu-smi` polling may be relatively slow on a heavily loaded host; the actual sample timestamps are saved.

TTFT is first streamed token time minus client request start, including queue time and first decode. Request TPOT is `(last token timestamp - first token timestamp)/(received tokens - 1)`. Multiple token IDs in the same SSE event have the **same timestamp**, because wire streaming cannot recover per-token execution times that were not streamed separately. Throughput is generated token IDs received within the 90-second measurement window divided by 90 seconds (excludes drain). For the **prefill** study, TTFT is a useful end-to-end indicator, but does not isolate pure prefill execution time from scheduling, queueing and first decode. For per-iteration execution, add vLLM internal tracing. Concurrency is closed-loop client count and not guaranteed to equal actual batch size; compare against `vllm:num_requests_running` and `num_requests_waiting`.

## Options and reproducibility

```
./experiment.sh plan --studies decode --models '*Qwen3*'
./experiment.sh start --studies prefill --models 'Qwen/Qwen3-4B' --max-runs 4
./experiment.sh start --foreground --max-runs 1
./experiment.sh resume
./experiment.sh report
python3 -m unittest discover -s tests -v
```

Edit `configs/models.json` for model selection and `configs/default.json` for image, timeouts, TP overrides, NPU memory utilization or vLLM flags; **rerun setup after changing the Docker image**. The pinned default is `quay.io/ascend/vllm-ascend:v0.32.0rc1-openeuler`, intended for Ascend A2/openEuler. A different driver/CANN version may require a compatible pinned image. Docker image SHA and original `npu-smi` output are saved to the setup inventory. The runner has a **28-minute maximum per configuration**, including model startup and measurements, before forced cleanup; first-time downloads of gated or slow models can fail and be resumed after troubleshooting.

### CPU-comparison cautions

The model list is extracted from both reports rather than the older `configs/default.json`, which had fewer models. Quantized model weights and Ascend quantization kernels may have different compatibility or execution paths; do not report an AWQ/F8/W8A8 failure as an accelerator performance result. Do not silently substitute another model or precision. Always report NPU count/TP, checkpoint ID, quantization, dtype, prompt/output token lengths and concurrency alongside CPU metrics. The CPU reports compare several Xeon recipe/manual configurations; select the corresponding per-model CPU rows when making your speedup plots.

References: https://docs.vllm.ai/projects/ascend/en/main/getting_started/installation.html and https://github.com/alannair/xeon6-vllm-decode-bench

The generated `logs/results.csv` also includes `server_itl_mean_ms_approx`: the difference in successive `vllm:inter_token_latency_seconds_sum` and `_count` histogram counter samples over the measured period. Its approximate window edges are limited by the 1-second Prometheus scrape interval, whereas client token timestamps are exact at receive time. Use this column against the CPU report's server ITL means, with the noted scrape-alignment caveat.

**NUMA:** `setup.sh` captures `numactl --hardware` (all eight host NUMA nodes) and the NPU inventory in `state/setup.json`. It does not assume NPU ID == CPU NUMA node ID or force host memory onto an unverified node. For serious NUMA-locality comparisons, determine the actual NPU-to-PCI/NUMA mapping and run a separate controlled host-locality study.
