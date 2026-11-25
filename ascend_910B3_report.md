# Ascend 910B3 vLLM benchmark report

Generated 2026-11-26 04:24 CST (UTC 20:24) while the controller is still running.

## Status

| Item | Value |
|---|---|
| Plan | `84b3da236a35` |
| Image | `quay.io/ascend/vllm-ascend:v0.32.0rc1-openeuler` |
| Planned runs | 940 (47 models × 20 configs) |
| Finished successfully | 503 |
| Finished failed | 141 |
| In progress | 1 |
| Not yet started | 295 |
| Controller | running, PID 3158929, elapsed 2 days 0 hours |
| Active container | `ascend910b3-bench-84b3da236a35-0644` |
| Active output | `/data2/alan/ascend910b3-vllm-bench/logs/Qwen__Qwen2.5-3B-Instruct/decode_tp1_in0032_out0512_clients016/attempt-20261125T202301300496Z` |

**Running now:** `Qwen/Qwen2.5-3B-Instruct` decode, TP=1, prompt 32, output 512, 16 clients (plan index 645/940). The server is loading weights. Decode configs already done for this model: concurrency 1, 2, 4, 8.

**Queued (not started):** 15 configs of the current model, then 280 configs across 14 models, in plan order. The in-progress config is separate from this table.

| Model | Configs left |
|---|---:|
| `Qwen/Qwen2.5-3B-Instruct` | 15 |
| `microsoft/Phi-4-mini-instruct` | 20 |
| `Qwen/Qwen3-4B-Instruct-2507` | 20 |
| `HuggingFaceH4/zephyr-7b-beta` | 20 |
| `allenai/OLMo-2-1124-7B-Instruct` | 20 |
| `Qwen/Qwen2.5-7B-Instruct` | 20 |
| `ibm-granite/granite-3.3-8b-instruct` | 20 |
| `01-ai/Yi-1.5-9B-Chat` | 20 |
| `allenai/OLMo-2-1124-13B-Instruct` | 20 |
| `microsoft/phi-4` | 20 |
| `Qwen/Qwen2.5-14B-Instruct` | 20 |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | 20 |
| `Qwen/Qwen3-30B-A3B-Instruct-2507` | 20 |
| `allenai/OLMo-2-0325-32B-Instruct` | 20 |
| `Qwen/Qwen3-32B` | 20 |

Failed configs are recorded and are not retried in this pass. `./experiment.sh resume` would retry anything that is not `done`, including the single `Qwen/Qwen3-30B-A3B` timeout and the unsupported quantization models.

## Results overview

One row per model whose planned configs are all recorded and that has at least one successful run. Decode throughput is generated tokens received in the 90-second window, divided by 90. TTFT and TPOT are client medians over completed requests. Prefill columns are median TTFT at concurrency 1. A dash means that config did not finish successfully.

| Model | TP | Decode tok/s c1 | c8 | c32 | c128 | Decode TPOT ms c1 | Prefill TTFT ms 256 | 1024 | 4096 | Done |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen/QwQ-32B` | 2 | 28.4 | 216.2 | 699.4 | 1456.4 | 33.60 | 139.1 | 261.6 | 928.6 | 20/20 |
| `Qwen/Qwen2.5-0.5B-Instruct` | 1 | 100.4 | 694.7 | 2270.2 | 5732.7 | 9.93 | 62.9 | 62.9 | 71.3 | 20/20 |
| `Qwen/Qwen3-1.7B` | 1 | 90.5 | 718.5 | 2325.0 | 5813.8 | 10.94 | 72.4 | 71.3 | 93.7 | 20/20 |
| `Qwen/Qwen3-14B` | 1 | 38.7 | 292.1 | 988.2 | 2276.8 | 25.77 | 82.7 | 156.3 | 587.2 | 20/20 |
| `Qwen/Qwen3-30B-A3B` | 2 | — | 464.7 | 1228.8 | 2905.5 | — | 186.3 | 186.9 | 245.8 | 19/20 |
| `Qwen/Qwen3-4B` | 1 | 84.0 | 661.6 | 2121.5 | 4962.3 | 11.92 | 94.0 | 99.1 | 205.5 | 20/20 |
| `Qwen/Qwen3-8B` | 1 | 66.8 | 486.2 | 1656.0 | 3640.9 | 14.90 | 95.1 | 96.1 | 325.4 | 20/20 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | 1 | 116.1 | 850.5 | 2855.6 | 7056.8 | 8.50 | 55.9 | 53.8 | 71.5 | 20/20 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | 1 | 97.2 | 744.5 | 2399.8 | 5557.3 | 10.30 | 79.2 | 84.5 | 124.0 | 20/20 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | 1 | 88.8 | 602.9 | 1948.9 | 4374.7 | 11.23 | 93.5 | 93.5 | 222.3 | 20/20 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | 1 | 86.5 | 606.3 | 1942.6 | 4369.1 | 11.51 | 96.3 | 98.4 | 222.1 | 20/20 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | 1 | 34.1 | 249.0 | 838.0 | 2067.1 | 28.79 | 130.0 | 188.4 | 769.3 | 20/20 |
| `ibm-granite/granite-3.2-2b-instruct` | 1 | 71.6 | 623.9 | 2007.2 | 4910.1 | 13.94 | 104.5 | 108.6 | 169.3 | 20/20 |
| `meta-llama/Llama-3.1-8B` | 1 | 61.2 | 419.7 | 1445.5 | 3534.1 | 16.30 | 93.1 | 99.8 | 330.4 | 20/20 |
| `meta-llama/Llama-3.1-8B-Instruct` | 1 | 61.3 | 420.0 | 1442.9 | 3537.1 | 16.24 | 89.7 | 98.4 | 330.3 | 20/20 |
| `meta-llama/Llama-3.2-1B` | 1 | 119.2 | 897.8 | 2818.1 | 6964.2 | 8.28 | 54.5 | 55.8 | 81.4 | 20/20 |
| `meta-llama/Llama-3.2-1B-Instruct` | 1 | 124.4 | 862.9 | 2815.7 | 7135.1 | 7.98 | 55.0 | 56.9 | 81.2 | 20/20 |
| `meta-llama/Llama-3.2-3B-Instruct` | 1 | 98.5 | 722.0 | 2286.1 | 5110.7 | 10.03 | 82.3 | 85.0 | 163.2 | 20/20 |
| `microsoft/Phi-4-reasoning` | 1 | 39.2 | 288.4 | 910.2 | 2184.5 | 25.45 | 97.7 | 159.0 | 598.9 | 20/20 |
| `zai-org/glm-4-9b-hf` | 1 | 43.8 | 257.8 | 890.4 | 2721.5 | 22.76 | 152.3 | 147.3 | 456.9 | 20/20 |
| `Qwen/Qwen3-0.6B` | 1 | 96.7 | 731.7 | 2318.6 | 5831.2 | 10.24 | 66.4 | 66.4 | 74.4 | 20/20 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | 1 | 109.5 | 760.8 | 2415.8 | 5261.8 | 9.08 | 74.4 | 75.5 | 93.4 | 20/20 |
| `Qwen/Qwen2.5-1.5B-Instruct` | 1 | 94.3 | 652.2 | 2063.2 | 5296.1 | 10.52 | 75.3 | 76.0 | 89.2 | 20/20 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 1 | 103.8 | 764.4 | 2305.2 | 3640.9 | 9.60 | 63.3 | 63.9 | 112.5 | 20/20 |
| `ibm-granite/granite-3.3-2b-instruct` | 1 | 80.6 | 590.2 | 2016.6 | 4843.8 | 12.20 | 111.1 | 111.2 | 168.0 | 20/20 |

## Failures

| Model | Configs | Cause |
|---|---:|---|
| `AMead10/Llama-3.2-1B-Instruct-AWQ` | 20 | auto_awq quantization is not supported on NPU |
| `AMead10/Llama-3.2-3B-Instruct-AWQ` | 20 | auto_awq quantization is not supported on NPU |
| `Qwen/QwQ-32B-AWQ` | 20 | auto_awq quantization is not supported on NPU |
| `Qwen/Qwen3-14B-AWQ` | 20 | auto_awq quantization is not supported on NPU |
| `Qwen/Qwen3-14B-FP8` | 20 | engine init failed: aclnnInplaceCopy error 561103 |
| `Qwen/Qwen3-30B-A3B` | 1 | first decode config timed out during startup; later 19 configs succeeded |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 20 | auto_awq quantization is not supported on NPU |
| `openai/gpt-oss-20b` | 20 | gpt_oss_mxfp4 quantization is not supported on NPU |

## All successful runs

Each row is one finished `done` configuration, including configs of the model that is still in progress. TPOT is the median per-request mean time per output token. Throughput excludes the drain window.

| Model | Study | TP | Prompt | Output | Clients | TTFT median ms | TPOT median ms | Tokens/s | Completed reqs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 1 | 56.0 | 33.60 | 28.4 | 5 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 2 | 123.8 | 34.18 | 56.9 | 10 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 4 | 119.8 | 34.76 | 113.8 | 20 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 8 | 183.6 | 36.68 | 216.2 | 40 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 16 | 285.1 | 39.70 | 364.1 | 64 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 32 | 376.3 | 45.00 | 699.4 | 128 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 64 | 592.4 | 53.33 | 1092.3 | 192 |
| `Qwen/QwQ-32B` | decode | 2 | 32 | 512 | 128 | 475.4 | 70.04 | 1456.4 | 256 |
| `Qwen/QwQ-32B` | prefill | 2 | 256 | 32 | 1 | 139.1 | 33.77 | 26.9 | 76 |
| `Qwen/QwQ-32B` | prefill | 2 | 256 | 32 | 8 | 442.7 | 41.24 | 148.3 | 424 |
| `Qwen/QwQ-32B` | prefill | 2 | 256 | 32 | 32 | 1172.6 | 62.98 | 318.3 | 911 |
| `Qwen/QwQ-32B` | prefill | 2 | 256 | 32 | 128 | 3763.3 | 177.0 | 446.9 | 1285 |
| `Qwen/QwQ-32B` | prefill | 2 | 1024 | 32 | 1 | 261.6 | 33.22 | 24.7 | 70 |
| `Qwen/QwQ-32B` | prefill | 2 | 1024 | 32 | 8 | 1612.9 | 44.62 | 85.3 | 246 |
| `Qwen/QwQ-32B` | prefill | 2 | 1024 | 32 | 32 | 3563.0 | 151.4 | 114.4 | 352 |
| `Qwen/QwQ-32B` | prefill | 2 | 1024 | 32 | 128 | 5325.0 | 784.3 | 119.8 | 384 |
| `Qwen/QwQ-32B` | prefill | 2 | 4096 | 32 | 1 | 928.6 | 34.30 | 16.0 | 46 |
| `Qwen/QwQ-32B` | prefill | 2 | 4096 | 32 | 8 | 2795.0 | 156.2 | 28.6 | 88 |
| `Qwen/QwQ-32B` | prefill | 2 | 4096 | 32 | 32 | 7253.8 | 771.4 | 27.3 | 96 |
| `Qwen/QwQ-32B` | prefill | 2 | 4096 | 32 | 128 | 34901.7 | 1004.9 | 25.5 | 73 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 1 | 38.5 | 9.93 | 100.4 | 18 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 2 | 59.2 | 9.97 | 198.3 | 36 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 4 | 66.6 | 10.34 | 351.9 | 64 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 8 | 93.8 | 10.38 | 694.7 | 128 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 16 | 107.9 | 11.77 | 1229.5 | 224 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 32 | 133.7 | 12.76 | 2270.2 | 416 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 64 | 217.5 | 15.05 | 3798.5 | 704 |
| `Qwen/Qwen2.5-0.5B-Instruct` | decode | 1 | 32 | 512 | 128 | 350.2 | 19.85 | 5732.7 | 1027 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 256 | 32 | 1 | 62.9 | 9.59 | 88.4 | 249 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 256 | 32 | 8 | 127.4 | 10.93 | 504.7 | 1424 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 256 | 32 | 32 | 171.5 | 12.85 | 1652.3 | 4672 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 256 | 32 | 128 | 417.8 | 22.15 | 3394.9 | 9638 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 62.9 | 9.18 | 90.9 | 256 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 136.3 | 10.60 | 507.8 | 1432 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 172.2 | 16.92 | 1353.8 | 3830 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 256.9 | 37.79 | 2597.5 | 7424 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 71.3 | 9.88 | 83.9 | 237 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 157.3 | 17.52 | 338.3 | 955 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 178.7 | 48.89 | 551.1 | 1568 |
| `Qwen/Qwen2.5-0.5B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 2714.0 | 79.59 | 718.4 | 2118 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 1 | 39.1 | 10.94 | 90.5 | 16 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 2 | 58.9 | 10.30 | 189.8 | 34 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 4 | 66.2 | 11.10 | 354.8 | 64 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 8 | 97.6 | 11.01 | 718.5 | 128 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 16 | 111.5 | 12.21 | 1286.2 | 240 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 32 | 164.3 | 13.47 | 2325.0 | 416 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 64 | 215.4 | 15.62 | 4000.3 | 705 |
| `Qwen/Qwen3-1.7B` | decode | 1 | 32 | 512 | 128 | 364.5 | 21.45 | 5813.8 | 1030 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 256 | 32 | 1 | 72.4 | 11.11 | 76.9 | 217 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 256 | 32 | 8 | 129.1 | 10.59 | 556.7 | 1568 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 256 | 32 | 32 | 242.2 | 13.19 | 1574.9 | 4448 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 256 | 32 | 128 | 509.1 | 28.60 | 2944.3 | 8399 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 1024 | 32 | 1 | 71.3 | 10.59 | 80.1 | 226 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 1024 | 32 | 8 | 199.7 | 10.53 | 486.1 | 1368 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 1024 | 32 | 32 | 309.2 | 21.14 | 1058.8 | 3008 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 1024 | 32 | 128 | 441.2 | 84.70 | 1316.7 | 3769 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 4096 | 32 | 1 | 93.7 | 9.83 | 79.3 | 224 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 4096 | 32 | 8 | 254.5 | 23.46 | 261.7 | 743 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 4096 | 32 | 32 | 456.6 | 89.81 | 310.1 | 890 |
| `Qwen/Qwen3-1.7B` | prefill | 1 | 4096 | 32 | 128 | 6451.6 | 193.9 | 316.1 | 986 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 1 | 55.3 | 25.77 | 38.7 | 7 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 2 | 83.4 | 25.79 | 77.2 | 14 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 4 | 75.6 | 26.31 | 151.3 | 28 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 8 | 113.8 | 27.20 | 292.1 | 56 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 16 | 162.2 | 28.77 | 546.1 | 96 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 32 | 227.2 | 31.99 | 988.2 | 192 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 64 | 405.7 | 37.31 | 1687.3 | 320 |
| `Qwen/Qwen3-14B` | decode | 1 | 32 | 512 | 128 | 622.6 | 47.80 | 2276.8 | 410 |
| `Qwen/Qwen3-14B` | prefill | 1 | 256 | 32 | 1 | 82.7 | 25.46 | 36.6 | 103 |
| `Qwen/Qwen3-14B` | prefill | 1 | 256 | 32 | 8 | 312.8 | 27.16 | 221.1 | 624 |
| `Qwen/Qwen3-14B` | prefill | 1 | 256 | 32 | 32 | 950.0 | 36.62 | 489.3 | 1408 |
| `Qwen/Qwen3-14B` | prefill | 1 | 256 | 32 | 128 | 2369.1 | 109.9 | 692.1 | 2048 |
| `Qwen/Qwen3-14B` | prefill | 1 | 1024 | 32 | 1 | 156.3 | 25.78 | 33.4 | 95 |
| `Qwen/Qwen3-14B` | prefill | 1 | 1024 | 32 | 8 | 1111.3 | 28.66 | 128.0 | 368 |
| `Qwen/Qwen3-14B` | prefill | 1 | 1024 | 32 | 32 | 2357.2 | 99.89 | 182.3 | 544 |
| `Qwen/Qwen3-14B` | prefill | 1 | 1024 | 32 | 128 | 3371.1 | 507.7 | 188.4 | 628 |
| `Qwen/Qwen3-14B` | prefill | 1 | 4096 | 32 | 1 | 587.2 | 26.65 | 22.6 | 64 |
| `Qwen/Qwen3-14B` | prefill | 1 | 4096 | 32 | 8 | 1794.8 | 124.8 | 44.1 | 128 |
| `Qwen/Qwen3-14B` | prefill | 1 | 4096 | 32 | 32 | 3677.6 | 515.8 | 45.8 | 149 |
| `Qwen/Qwen3-14B` | prefill | 1 | 4096 | 32 | 128 | 39647.7 | 649.4 | 42.4 | 123 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 2 | 81.1 | 15.45 | 127.6 | 24 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 4 | 88.2 | 14.73 | 267.5 | 48 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 8 | 92.2 | 17.00 | 464.7 | 88 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 16 | 127.9 | 20.67 | 765.2 | 144 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 32 | 269.0 | 25.47 | 1228.8 | 224 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 64 | 516.5 | 31.36 | 1972.0 | 384 |
| `Qwen/Qwen3-30B-A3B` | decode | 2 | 32 | 512 | 128 | 599.3 | 42.47 | 2905.5 | 512 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 256 | 32 | 1 | 186.3 | 14.79 | 49.3 | 139 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 256 | 32 | 8 | 385.4 | 21.37 | 244.6 | 693 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 256 | 32 | 32 | 573.7 | 38.72 | 558.1 | 1600 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 256 | 32 | 128 | 651.4 | 98.93 | 1054.5 | 3072 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 1024 | 32 | 1 | 186.9 | 15.72 | 47.2 | 133 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 1024 | 32 | 8 | 505.6 | 20.66 | 232.4 | 656 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 1024 | 32 | 32 | 793.6 | 52.48 | 420.0 | 1189 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 1024 | 32 | 128 | 1257.0 | 199.8 | 511.6 | 1536 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 4096 | 32 | 1 | 245.8 | 14.20 | 46.4 | 131 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 4096 | 32 | 8 | 690.9 | 51.99 | 110.9 | 318 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 4096 | 32 | 32 | 1325.6 | 197.1 | 127.3 | 383 |
| `Qwen/Qwen3-30B-A3B` | prefill | 2 | 4096 | 32 | 128 | 15083.4 | 456.1 | 126.6 | 372 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 1 | 44.6 | 11.92 | 84.0 | 15 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 2 | 70.9 | 12.69 | 156.1 | 28 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 4 | 78.1 | 12.59 | 314.1 | 56 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 8 | 116.2 | 11.65 | 661.6 | 120 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 16 | 172.9 | 13.23 | 1173.1 | 208 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 32 | 181.2 | 14.63 | 2121.5 | 384 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 64 | 260.7 | 18.05 | 3450.5 | 640 |
| `Qwen/Qwen3-4B` | decode | 1 | 32 | 512 | 128 | 408.1 | 25.15 | 4962.3 | 896 |
| `Qwen/Qwen3-4B` | prefill | 1 | 256 | 32 | 1 | 94.0 | 11.50 | 71.2 | 201 |
| `Qwen/Qwen3-4B` | prefill | 1 | 256 | 32 | 8 | 187.6 | 12.43 | 440.8 | 1242 |
| `Qwen/Qwen3-4B` | prefill | 1 | 256 | 32 | 32 | 434.6 | 14.54 | 1149.2 | 3264 |
| `Qwen/Qwen3-4B` | prefill | 1 | 256 | 32 | 128 | 561.9 | 47.95 | 1973.3 | 5632 |
| `Qwen/Qwen3-4B` | prefill | 1 | 1024 | 32 | 1 | 99.1 | 12.53 | 65.8 | 186 |
| `Qwen/Qwen3-4B` | prefill | 1 | 1024 | 32 | 8 | 387.9 | 12.12 | 335.1 | 944 |
| `Qwen/Qwen3-4B` | prefill | 1 | 1024 | 32 | 32 | 733.2 | 37.08 | 538.8 | 1536 |
| `Qwen/Qwen3-4B` | prefill | 1 | 1024 | 32 | 128 | 1072.1 | 175.6 | 599.9 | 1788 |
| `Qwen/Qwen3-4B` | prefill | 1 | 4096 | 32 | 1 | 205.5 | 11.54 | 56.8 | 160 |
| `Qwen/Qwen3-4B` | prefill | 1 | 4096 | 32 | 8 | 618.7 | 47.07 | 122.4 | 351 |
| `Qwen/Qwen3-4B` | prefill | 1 | 4096 | 32 | 32 | 1254.0 | 186.2 | 137.6 | 407 |
| `Qwen/Qwen3-4B` | prefill | 1 | 4096 | 32 | 128 | 14329.2 | 433.4 | 135.4 | 398 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 1 | 44.7 | 14.90 | 66.8 | 12 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 2 | 73.0 | 14.99 | 132.3 | 24 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 4 | 67.2 | 15.49 | 256.4 | 48 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 8 | 120.2 | 16.24 | 486.2 | 88 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 16 | 170.2 | 17.18 | 913.6 | 176 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 32 | 191.4 | 18.95 | 1656.0 | 320 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 64 | 272.9 | 23.70 | 2647.4 | 512 |
| `Qwen/Qwen3-8B` | decode | 1 | 32 | 512 | 128 | 449.3 | 32.33 | 3640.9 | 640 |
| `Qwen/Qwen3-8B` | prefill | 1 | 256 | 32 | 1 | 95.1 | 14.58 | 58.3 | 164 |
| `Qwen/Qwen3-8B` | prefill | 1 | 256 | 32 | 8 | 217.6 | 16.15 | 355.6 | 1008 |
| `Qwen/Qwen3-8B` | prefill | 1 | 256 | 32 | 32 | 619.1 | 18.97 | 842.0 | 2400 |
| `Qwen/Qwen3-8B` | prefill | 1 | 256 | 32 | 128 | 1318.1 | 66.03 | 1231.2 | 3584 |
| `Qwen/Qwen3-8B` | prefill | 1 | 1024 | 32 | 1 | 96.1 | 14.82 | 57.5 | 162 |
| `Qwen/Qwen3-8B` | prefill | 1 | 1024 | 32 | 8 | 594.5 | 17.41 | 224.7 | 640 |
| `Qwen/Qwen3-8B` | prefill | 1 | 1024 | 32 | 32 | 1255.1 | 56.40 | 339.3 | 960 |
| `Qwen/Qwen3-8B` | prefill | 1 | 1024 | 32 | 128 | 1782.1 | 280.2 | 367.7 | 1121 |
| `Qwen/Qwen3-8B` | prefill | 1 | 4096 | 32 | 1 | 325.4 | 15.68 | 39.4 | 111 |
| `Qwen/Qwen3-8B` | prefill | 1 | 4096 | 32 | 8 | 987.4 | 71.80 | 79.5 | 227 |
| `Qwen/Qwen3-8B` | prefill | 1 | 4096 | 32 | 32 | 1974.0 | 287.9 | 88.0 | 260 |
| `Qwen/Qwen3-8B` | prefill | 1 | 4096 | 32 | 128 | 24325.7 | 615.0 | 82.0 | 238 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 1 | 31.3 | 8.50 | 116.1 | 21 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 2 | 48.4 | 8.56 | 231.6 | 42 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 4 | 53.0 | 8.64 | 456.3 | 84 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 8 | 83.0 | 9.30 | 850.5 | 152 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 16 | 94.4 | 9.56 | 1627.8 | 288 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 32 | 140.9 | 10.95 | 2855.6 | 512 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 64 | 203.6 | 12.92 | 4816.2 | 896 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 128 | 339.4 | 17.52 | 7056.8 | 1281 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 1 | 55.9 | 8.16 | 103.4 | 291 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 8 | 105.2 | 8.50 | 690.3 | 1944 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 32 | 178.2 | 10.26 | 2059.4 | 5824 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 128 | 415.4 | 21.09 | 3901.1 | 11010 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 1 | 53.8 | 7.68 | 109.1 | 307 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 8 | 143.6 | 8.57 | 622.9 | 1760 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 32 | 187.0 | 16.09 | 1490.6 | 4224 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 128 | 398.5 | 50.06 | 2058.0 | 5892 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 1 | 71.5 | 7.75 | 101.4 | 286 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 8 | 151.6 | 17.51 | 367.1 | 1040 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 32 | 198.6 | 60.88 | 483.4 | 1376 |
| `RedHatAI/Llama-3.2-1B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 128 | 4147.9 | 124.8 | 495.3 | 1490 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 1 | 40.2 | 10.30 | 97.2 | 18 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 2 | 61.4 | 10.15 | 193.4 | 34 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 4 | 67.5 | 10.62 | 374.3 | 68 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 8 | 113.3 | 10.50 | 744.5 | 136 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 16 | 125.8 | 11.27 | 1390.8 | 256 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 32 | 200.3 | 12.96 | 2399.8 | 448 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 64 | 239.1 | 16.18 | 3856.2 | 704 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 128 | 408.1 | 22.39 | 5557.3 | 1024 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 1 | 79.2 | 9.62 | 83.8 | 236 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 8 | 155.1 | 10.37 | 534.8 | 1512 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 32 | 292.9 | 12.47 | 1501.9 | 4256 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 128 | 450.6 | 35.58 | 2600.8 | 7438 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 1 | 84.5 | 9.88 | 81.8 | 231 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 8 | 249.9 | 10.24 | 451.3 | 1272 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 32 | 404.3 | 26.18 | 839.9 | 2368 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 128 | 565.3 | 107.8 | 1034.7 | 2959 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 1 | 124.0 | 9.46 | 76.1 | 215 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 8 | 331.5 | 29.47 | 204.7 | 580 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 32 | 674.6 | 110.1 | 242.9 | 704 |
| `RedHatAI/Llama-3.2-3B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 128 | 8140.1 | 245.3 | 247.6 | 794 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 1 | 49.4 | 11.23 | 88.8 | 16 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 2 | 72.9 | 11.38 | 173.6 | 32 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 4 | 71.8 | 11.84 | 333.1 | 60 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 8 | 119.1 | 13.05 | 602.9 | 112 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 16 | 192.4 | 14.46 | 1080.7 | 192 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 32 | 175.7 | 16.09 | 1948.9 | 352 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 64 | 259.7 | 20.83 | 2999.3 | 576 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | decode | 1 | 32 | 512 | 128 | 433.2 | 28.47 | 4374.7 | 811 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 1 | 93.5 | 10.51 | 75.2 | 212 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 8 | 176.7 | 13.02 | 440.2 | 1240 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 32 | 325.8 | 19.25 | 1092.5 | 3104 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 256 | 32 | 128 | 646.5 | 52.99 | 1774.8 | 5081 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 1 | 93.5 | 10.43 | 76.1 | 215 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 8 | 411.3 | 14.10 | 301.4 | 849 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 32 | 793.8 | 41.07 | 489.5 | 1408 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 1024 | 32 | 128 | 1167.1 | 188.8 | 554.4 | 1661 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 1 | 222.3 | 11.18 | 56.1 | 158 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 8 | 631.4 | 49.41 | 116.9 | 336 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 32 | 1277.7 | 192.1 | 134.4 | 392 |
| `RedHatAI/Meta-Llama-3.1-8B-Instruct-quantized.w8a8` | prefill | 1 | 4096 | 32 | 128 | 14803.3 | 446.5 | 130.2 | 382 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 1 | 49.0 | 11.51 | 86.5 | 16 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 2 | 72.2 | 11.39 | 172.6 | 32 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 4 | 71.4 | 11.82 | 333.9 | 60 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 8 | 124.4 | 12.97 | 606.3 | 112 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 16 | 137.2 | 14.43 | 1090.7 | 192 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 32 | 186.0 | 16.13 | 1942.6 | 352 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 64 | 278.9 | 20.92 | 2988.0 | 576 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | decode | 1 | 32 | 512 | 128 | 426.5 | 28.34 | 4369.1 | 768 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 256 | 32 | 1 | 96.3 | 10.93 | 73.8 | 208 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 256 | 32 | 8 | 177.8 | 12.88 | 442.1 | 1248 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 256 | 32 | 32 | 419.5 | 16.64 | 1092.3 | 3104 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 256 | 32 | 128 | 804.6 | 47.76 | 1776.3 | 5120 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 1 | 98.4 | 10.82 | 73.7 | 208 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 8 | 408.6 | 14.00 | 302.9 | 856 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 32 | 794.1 | 41.40 | 489.3 | 1405 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 128 | 1166.6 | 188.7 | 554.9 | 1664 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 1 | 222.1 | 11.23 | 55.9 | 158 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 8 | 631.3 | 49.42 | 116.8 | 336 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 32 | 1276.1 | 192.1 | 134.4 | 392 |
| `RedHatAI/Meta-Llama-3.1-8B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 128 | 14799.5 | 446.2 | 130.2 | 382 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 1 | 68.1 | 28.79 | 34.1 | 6 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 2 | 120.4 | 29.29 | 67.9 | 12 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 4 | 104.4 | 30.35 | 131.1 | 24 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 8 | 189.9 | 31.82 | 249.0 | 48 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 16 | 187.5 | 33.58 | 455.1 | 80 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 32 | 286.4 | 37.68 | 838.0 | 160 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 64 | 473.2 | 44.86 | 1405.6 | 256 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | decode | 1 | 32 | 512 | 128 | 1200.4 | 59.86 | 2067.1 | 384 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 256 | 32 | 1 | 130.0 | 28.54 | 31.5 | 89 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 256 | 32 | 8 | 423.9 | 31.74 | 181.4 | 512 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 256 | 32 | 32 | 1421.0 | 37.21 | 396.1 | 1120 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 256 | 32 | 128 | 2981.4 | 141.5 | 547.2 | 1664 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 1 | 188.4 | 28.86 | 29.5 | 84 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 8 | 1396.8 | 33.82 | 103.9 | 296 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 32 | 3002.8 | 125.7 | 147.8 | 438 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 1024 | 32 | 128 | 15712.1 | 325.8 | 151.8 | 448 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 1 | 769.3 | 30.32 | 18.6 | 53 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 8 | 2305.2 | 159.5 | 34.2 | 102 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 32 | 16564.8 | 339.2 | 36.0 | 103 |
| `RedHatAI/QwQ-32B-quantized.w8a8` | prefill | 1 | 4096 | 32 | 128 | 42790.5 | 339.5 | 35.9 | 102 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 1 | 53.0 | 13.94 | 71.6 | 13 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 2 | 84.6 | 13.31 | 148.5 | 28 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 4 | 81.3 | 12.03 | 327.3 | 60 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 8 | 137.5 | 12.56 | 623.9 | 112 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 16 | 162.6 | 14.08 | 1110.6 | 208 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 32 | 188.2 | 15.56 | 2007.2 | 384 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 64 | 275.1 | 18.43 | 3375.6 | 640 |
| `ibm-granite/granite-3.2-2b-instruct` | decode | 1 | 32 | 512 | 128 | 403.1 | 25.32 | 4910.1 | 896 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 256 | 32 | 1 | 104.5 | 12.15 | 66.0 | 186 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 256 | 32 | 8 | 209.6 | 13.19 | 415.3 | 1176 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 256 | 32 | 32 | 376.9 | 14.74 | 1220.6 | 3456 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 256 | 32 | 128 | 490.9 | 40.74 | 2323.6 | 6656 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 1024 | 32 | 1 | 108.6 | 12.21 | 65.7 | 185 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 1024 | 32 | 8 | 339.1 | 12.11 | 355.6 | 1008 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 1024 | 32 | 32 | 570.3 | 32.97 | 637.7 | 1824 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 1024 | 32 | 128 | 818.1 | 147.0 | 735.2 | 2161 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 4096 | 32 | 1 | 169.3 | 11.42 | 61.0 | 172 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 4096 | 32 | 8 | 472.5 | 38.02 | 153.7 | 439 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 4096 | 32 | 32 | 977.8 | 151.0 | 171.8 | 502 |
| `ibm-granite/granite-3.2-2b-instruct` | prefill | 1 | 4096 | 32 | 128 | 11738.9 | 354.5 | 168.4 | 499 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 1 | 41.1 | 16.30 | 61.2 | 11 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 2 | 70.7 | 17.10 | 116.1 | 22 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 4 | 64.3 | 17.63 | 225.7 | 40 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 8 | 114.7 | 18.85 | 419.7 | 80 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 16 | 174.9 | 19.88 | 792.8 | 144 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 32 | 176.3 | 21.83 | 1445.5 | 256 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 64 | 261.8 | 27.04 | 2330.0 | 448 |
| `meta-llama/Llama-3.1-8B` | decode | 1 | 32 | 512 | 128 | 514.3 | 35.38 | 3534.1 | 640 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 256 | 32 | 1 | 93.1 | 16.01 | 54.2 | 153 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 256 | 32 | 8 | 220.5 | 18.82 | 318.2 | 896 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 256 | 32 | 32 | 572.2 | 23.64 | 784.0 | 2208 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 256 | 32 | 128 | 1389.9 | 64.72 | 1185.1 | 3456 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 1024 | 32 | 1 | 99.8 | 16.33 | 52.7 | 149 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 1024 | 32 | 8 | 607.9 | 19.84 | 208.0 | 592 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 1024 | 32 | 32 | 1275.3 | 59.36 | 323.7 | 928 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 1024 | 32 | 128 | 1829.5 | 286.2 | 363.9 | 1097 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 4096 | 32 | 1 | 330.4 | 16.99 | 37.3 | 105 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 4096 | 32 | 8 | 976.1 | 73.13 | 77.1 | 224 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 4096 | 32 | 32 | 1981.0 | 288.5 | 88.0 | 260 |
| `meta-llama/Llama-3.1-8B` | prefill | 1 | 4096 | 32 | 128 | 22315.9 | 675.2 | 80.2 | 233 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 1 | 42.1 | 16.24 | 61.3 | 11 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 2 | 69.7 | 17.14 | 116.0 | 22 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 4 | 67.8 | 17.54 | 226.6 | 40 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 8 | 113.9 | 18.84 | 420.0 | 80 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 16 | 165.2 | 19.89 | 792.6 | 144 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 32 | 206.0 | 21.82 | 1442.9 | 256 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 64 | 282.8 | 27.03 | 2325.3 | 448 |
| `meta-llama/Llama-3.1-8B-Instruct` | decode | 1 | 32 | 512 | 128 | 487.5 | 35.40 | 3537.1 | 640 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 256 | 32 | 1 | 89.7 | 16.02 | 54.4 | 154 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 256 | 32 | 8 | 218.8 | 18.83 | 318.6 | 904 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 256 | 32 | 32 | 640.9 | 21.59 | 776.2 | 2208 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 256 | 32 | 128 | 1243.5 | 68.84 | 1184.5 | 3456 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 98.4 | 16.31 | 52.9 | 149 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 608.6 | 19.89 | 207.7 | 592 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 1278.7 | 59.27 | 325.5 | 928 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 1825.6 | 286.3 | 363.9 | 1097 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 330.3 | 16.98 | 37.3 | 105 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 976.1 | 72.88 | 77.1 | 224 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 1975.9 | 287.7 | 88.0 | 260 |
| `meta-llama/Llama-3.1-8B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 22257.5 | 673.6 | 80.2 | 233 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 1 | 30.6 | 8.28 | 119.2 | 21 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 2 | 46.7 | 8.19 | 239.6 | 44 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 4 | 51.4 | 8.50 | 462.7 | 84 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 8 | 81.6 | 8.73 | 897.8 | 160 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 16 | 93.3 | 9.72 | 1617.3 | 288 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 32 | 146.4 | 11.15 | 2818.1 | 512 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 64 | 195.8 | 13.11 | 4734.2 | 864 |
| `meta-llama/Llama-3.2-1B` | decode | 1 | 32 | 512 | 128 | 355.5 | 17.54 | 6964.2 | 1280 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 256 | 32 | 1 | 54.5 | 7.84 | 106.4 | 300 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 256 | 32 | 8 | 111.0 | 8.60 | 675.7 | 1904 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 256 | 32 | 32 | 204.0 | 10.59 | 1920.4 | 5408 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 256 | 32 | 128 | 478.0 | 21.49 | 3550.8 | 10114 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 1024 | 32 | 1 | 55.8 | 7.85 | 106.9 | 301 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 1024 | 32 | 8 | 168.4 | 9.02 | 574.6 | 1624 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 1024 | 32 | 32 | 237.6 | 17.50 | 1311.4 | 3712 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 1024 | 32 | 128 | 601.2 | 56.94 | 1735.9 | 5007 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 4096 | 32 | 1 | 81.4 | 8.04 | 96.5 | 272 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 4096 | 32 | 8 | 198.4 | 17.97 | 336.0 | 952 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 4096 | 32 | 32 | 287.2 | 69.03 | 415.4 | 1184 |
| `meta-llama/Llama-3.2-1B` | prefill | 1 | 4096 | 32 | 128 | 4856.1 | 146.2 | 421.3 | 1282 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 1 | 29.9 | 7.98 | 124.4 | 22 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 2 | 48.3 | 8.53 | 232.0 | 42 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 4 | 50.1 | 8.20 | 475.8 | 84 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 8 | 86.3 | 9.11 | 862.9 | 152 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 16 | 92.3 | 9.28 | 1687.7 | 304 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 32 | 151.1 | 11.10 | 2815.7 | 512 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 64 | 208.0 | 13.37 | 4667.6 | 833 |
| `meta-llama/Llama-3.2-1B-Instruct` | decode | 1 | 32 | 512 | 128 | 333.4 | 17.27 | 7135.1 | 1281 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 256 | 32 | 1 | 55.0 | 7.80 | 106.2 | 299 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 256 | 32 | 8 | 104.4 | 8.25 | 708.7 | 2000 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 256 | 32 | 32 | 200.6 | 10.39 | 1956.7 | 5512 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 256 | 32 | 128 | 481.3 | 21.85 | 3563.9 | 10114 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 56.9 | 8.22 | 101.5 | 286 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 163.4 | 8.20 | 610.4 | 1720 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 251.2 | 17.21 | 1309.1 | 3712 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 484.8 | 59.58 | 1735.3 | 4992 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 81.2 | 7.84 | 98.0 | 276 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 198.1 | 18.51 | 330.2 | 936 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 229.6 | 70.90 | 415.0 | 1184 |
| `meta-llama/Llama-3.2-1B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 4861.5 | 146.3 | 421.3 | 1282 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 1 | 39.5 | 10.03 | 98.5 | 18 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 2 | 62.9 | 10.61 | 186.2 | 34 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 4 | 66.7 | 11.09 | 357.7 | 64 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 8 | 101.6 | 10.84 | 722.0 | 128 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 16 | 158.4 | 12.21 | 1274.7 | 240 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 32 | 197.3 | 13.64 | 2286.1 | 416 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 64 | 247.6 | 17.09 | 3644.4 | 704 |
| `meta-llama/Llama-3.2-3B-Instruct` | decode | 1 | 32 | 512 | 128 | 386.6 | 23.94 | 5110.7 | 905 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 256 | 32 | 1 | 82.3 | 9.88 | 82.2 | 232 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 256 | 32 | 8 | 145.4 | 10.53 | 537.6 | 1520 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 256 | 32 | 32 | 228.4 | 16.51 | 1388.1 | 3936 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 256 | 32 | 128 | 477.8 | 40.45 | 2338.4 | 6656 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 85.0 | 9.90 | 80.8 | 228 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 302.8 | 11.61 | 385.3 | 1088 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 564.1 | 31.94 | 651.9 | 1856 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 782.5 | 139.7 | 776.9 | 2268 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 163.2 | 9.95 | 67.7 | 191 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 456.7 | 37.62 | 156.5 | 447 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 913.7 | 141.2 | 184.1 | 539 |
| `meta-llama/Llama-3.2-3B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 10680.6 | 321.6 | 186.3 | 555 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 1 | 50.6 | 25.45 | 39.2 | 7 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 2 | 87.2 | 25.83 | 77.1 | 14 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 4 | 77.9 | 26.26 | 151.7 | 28 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 8 | 132.4 | 27.52 | 288.4 | 56 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 16 | 191.8 | 29.40 | 538.7 | 96 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 32 | 237.5 | 33.20 | 910.2 | 160 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 64 | 330.1 | 39.71 | 1456.4 | 256 |
| `microsoft/Phi-4-reasoning` | decode | 1 | 32 | 512 | 128 | 672.8 | 51.33 | 2184.5 | 384 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 256 | 32 | 1 | 97.7 | 25.22 | 36.3 | 103 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 256 | 32 | 8 | 330.7 | 27.40 | 216.2 | 616 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 256 | 32 | 32 | 1127.9 | 33.12 | 467.9 | 1344 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 256 | 32 | 128 | 2545.8 | 108.4 | 682.9 | 2038 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 1024 | 32 | 1 | 159.0 | 25.82 | 33.3 | 94 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 1024 | 32 | 8 | 1129.2 | 29.09 | 125.2 | 360 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 1024 | 32 | 32 | 2412.6 | 103.6 | 181.7 | 527 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 1024 | 32 | 128 | 5698.4 | 457.8 | 188.8 | 616 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 4096 | 32 | 1 | 598.9 | 27.04 | 22.2 | 63 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 4096 | 32 | 8 | 1858.5 | 129.1 | 42.8 | 127 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 4096 | 32 | 32 | 4852.5 | 524.5 | 41.8 | 144 |
| `microsoft/Phi-4-reasoning` | prefill | 1 | 4096 | 32 | 128 | 42148.8 | 525.6 | 41.1 | 124 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 1 | 54.0 | 22.76 | 43.8 | 8 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 2 | 85.8 | 28.42 | 68.3 | 12 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 4 | 86.7 | 28.99 | 136.5 | 24 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 8 | 168.6 | 30.74 | 257.8 | 48 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 16 | 263.5 | 32.51 | 455.1 | 80 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 32 | 274.0 | 35.45 | 890.4 | 160 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 64 | 334.5 | 39.59 | 1456.4 | 256 |
| `zai-org/glm-4-9b-hf` | decode | 1 | 32 | 512 | 128 | 595.7 | 45.91 | 2721.5 | 512 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 256 | 32 | 1 | 152.3 | 22.53 | 37.6 | 106 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 256 | 32 | 8 | 324.5 | 30.30 | 202.0 | 576 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 256 | 32 | 32 | 893.1 | 35.34 | 512.0 | 1472 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 256 | 32 | 128 | 1789.2 | 92.90 | 883.1 | 2560 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 1024 | 32 | 1 | 147.3 | 22.04 | 38.3 | 108 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 1024 | 32 | 8 | 850.2 | 31.10 | 139.9 | 400 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 1024 | 32 | 32 | 1726.4 | 82.42 | 238.3 | 680 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 1024 | 32 | 128 | 2429.0 | 370.5 | 273.1 | 843 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 4096 | 32 | 1 | 456.9 | 22.53 | 27.6 | 78 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 4096 | 32 | 8 | 1325.0 | 98.40 | 57.1 | 168 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 4096 | 32 | 32 | 2599.8 | 373.2 | 67.2 | 203 |
| `zai-org/glm-4-9b-hf` | prefill | 1 | 4096 | 32 | 128 | 28754.7 | 870.8 | 57.1 | 165 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 1 | 38.6 | 10.24 | 96.7 | 18 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 2 | 61.1 | 11.17 | 177.0 | 32 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 4 | 62.1 | 10.11 | 384.8 | 68 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 8 | 95.7 | 10.78 | 731.7 | 136 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 16 | 109.5 | 11.63 | 1352.8 | 240 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 32 | 168.8 | 13.43 | 2318.6 | 416 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 64 | 224.5 | 16.27 | 3849.5 | 704 |
| `Qwen/Qwen3-0.6B` | decode | 1 | 32 | 512 | 128 | 365.6 | 21.07 | 5831.2 | 1028 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 256 | 32 | 1 | 66.4 | 10.02 | 84.6 | 238 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 256 | 32 | 8 | 127.5 | 10.56 | 561.3 | 1584 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 256 | 32 | 32 | 174.7 | 12.65 | 1800.2 | 5088 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 256 | 32 | 128 | 443.3 | 23.56 | 3473.4 | 9897 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 1024 | 32 | 1 | 66.4 | 9.85 | 85.5 | 241 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 1024 | 32 | 8 | 145.6 | 11.17 | 517.7 | 1464 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 1024 | 32 | 32 | 176.1 | 16.92 | 1444.6 | 4079 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 1024 | 32 | 128 | 246.5 | 52.45 | 2176.3 | 6173 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 4096 | 32 | 1 | 74.4 | 10.37 | 81.2 | 229 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 4096 | 32 | 8 | 159.3 | 17.88 | 355.6 | 1006 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 4096 | 32 | 32 | 191.6 | 59.05 | 502.5 | 1431 |
| `Qwen/Qwen3-0.6B` | prefill | 1 | 4096 | 32 | 128 | 3929.6 | 118.0 | 525.7 | 1576 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 1 | 36.2 | 9.08 | 109.5 | 20 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 2 | 58.1 | 9.79 | 203.0 | 36 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 4 | 62.3 | 9.98 | 395.4 | 72 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 8 | 102.5 | 10.26 | 760.8 | 136 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 16 | 114.9 | 10.73 | 1465.6 | 272 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 32 | 149.0 | 12.99 | 2415.8 | 448 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 64 | 207.7 | 15.34 | 4074.8 | 768 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | decode | 1 | 32 | 512 | 128 | 379.5 | 23.56 | 5261.8 | 1024 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 256 | 32 | 1 | 74.4 | 9.64 | 85.6 | 241 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 256 | 32 | 8 | 141.4 | 9.78 | 572.3 | 1616 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 256 | 32 | 32 | 239.9 | 11.55 | 1706.7 | 4832 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 256 | 32 | 128 | 437.1 | 31.78 | 2895.3 | 8224 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 1024 | 32 | 1 | 75.5 | 9.40 | 87.2 | 246 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 1024 | 32 | 8 | 202.0 | 9.58 | 512.3 | 1448 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 1024 | 32 | 32 | 308.2 | 23.38 | 989.9 | 2813 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 1024 | 32 | 128 | 460.1 | 95.14 | 1182.7 | 3399 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 4096 | 32 | 1 | 93.4 | 9.64 | 80.5 | 227 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 4096 | 32 | 8 | 255.8 | 25.83 | 241.7 | 685 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 4096 | 32 | 32 | 518.4 | 96.47 | 288.3 | 832 |
| `deepseek-ai/deepseek-coder-1.3b-instruct` | prefill | 1 | 4096 | 32 | 128 | 7351.4 | 197.0 | 294.8 | 928 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 1 | 40.7 | 10.52 | 94.3 | 17 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 2 | 62.6 | 10.11 | 194.3 | 36 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 4 | 70.7 | 10.91 | 335.9 | 60 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 8 | 103.6 | 10.86 | 652.2 | 120 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 16 | 116.5 | 11.78 | 1231.4 | 224 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 32 | 151.2 | 14.03 | 2063.2 | 384 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 64 | 255.7 | 16.56 | 3501.9 | 640 |
| `Qwen/Qwen2.5-1.5B-Instruct` | decode | 1 | 32 | 512 | 128 | 387.4 | 21.50 | 5296.1 | 1024 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 256 | 32 | 1 | 75.3 | 10.81 | 77.5 | 219 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 256 | 32 | 8 | 148.0 | 11.63 | 463.6 | 1312 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 256 | 32 | 32 | 239.9 | 12.80 | 1471.3 | 4160 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 256 | 32 | 128 | 520.4 | 29.03 | 2666.0 | 7584 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 76.0 | 10.57 | 79.0 | 223 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 201.4 | 11.68 | 418.5 | 1184 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 284.3 | 21.29 | 996.7 | 2816 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 552.3 | 66.10 | 1420.6 | 4096 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 89.2 | 10.01 | 79.5 | 224 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 194.6 | 22.23 | 266.5 | 752 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 311.2 | 72.54 | 360.7 | 1031 |
| `Qwen/Qwen2.5-1.5B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 5295.7 | 155.8 | 362.2 | 1117 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 1 | 36.4 | 9.60 | 103.8 | 19 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 2 | 58.7 | 9.85 | 196.2 | 36 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 4 | 63.2 | 10.08 | 392.3 | 72 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 8 | 91.5 | 10.18 | 764.4 | 136 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 16 | 104.5 | 11.11 | 1411.9 | 256 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 32 | 130.0 | 13.73 | 2305.2 | 416 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 64 | 204.2 | 17.83 | 3537.5 | 640 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | decode | 1 | 32 | 512 | 128 | 343.6 | 33.06 | 3640.9 | 640 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 256 | 32 | 1 | 63.3 | 9.61 | 87.6 | 247 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 256 | 32 | 8 | 117.7 | 9.85 | 604.3 | 1704 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 256 | 32 | 32 | 257.7 | 12.05 | 1622.5 | 4576 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 256 | 32 | 128 | 559.2 | 40.12 | 2273.2 | 6503 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 1024 | 32 | 1 | 63.9 | 9.33 | 89.3 | 252 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 1024 | 32 | 8 | 224.8 | 10.37 | 466.5 | 1320 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 1024 | 32 | 32 | 392.7 | 29.19 | 785.3 | 2240 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 1024 | 32 | 128 | 629.9 | 133.6 | 839.8 | 2432 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 4096 | 32 | 1 | 112.5 | 9.29 | 80.0 | 226 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 4096 | 32 | 8 | 325.2 | 32.57 | 190.7 | 543 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 4096 | 32 | 32 | 718.9 | 131.3 | 205.8 | 595 |
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | prefill | 1 | 4096 | 32 | 128 | 10696.0 | 278.6 | 203.4 | 611 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 1 | 48.3 | 12.20 | 80.6 | 15 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 2 | 78.2 | 12.27 | 160.2 | 30 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 4 | 84.2 | 13.46 | 289.3 | 52 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 8 | 141.7 | 13.12 | 590.2 | 104 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 16 | 161.0 | 14.27 | 1094.9 | 208 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 32 | 205.1 | 15.48 | 2016.6 | 384 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 64 | 280.1 | 18.15 | 3422.0 | 640 |
| `ibm-granite/granite-3.3-2b-instruct` | decode | 1 | 32 | 512 | 128 | 401.8 | 25.74 | 4843.8 | 896 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 256 | 32 | 1 | 111.1 | 12.56 | 63.6 | 180 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 256 | 32 | 8 | 200.4 | 12.72 | 426.0 | 1200 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 256 | 32 | 32 | 374.6 | 14.72 | 1222.1 | 3456 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 256 | 32 | 128 | 594.7 | 39.04 | 2265.6 | 6402 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 1024 | 32 | 1 | 111.2 | 12.32 | 64.7 | 183 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 1024 | 32 | 8 | 340.7 | 13.65 | 333.8 | 944 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 1024 | 32 | 32 | 568.4 | 32.45 | 648.2 | 1839 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 1024 | 32 | 128 | 817.5 | 147.1 | 735.2 | 2161 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 4096 | 32 | 1 | 168.0 | 11.63 | 60.1 | 170 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 4096 | 32 | 8 | 472.1 | 37.96 | 153.8 | 440 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 4096 | 32 | 32 | 975.8 | 150.5 | 172.1 | 504 |
| `ibm-granite/granite-3.3-2b-instruct` | prefill | 1 | 4096 | 32 | 128 | 11724.2 | 354.0 | 168.4 | 499 |
| `Qwen/Qwen2.5-3B-Instruct` | decode | 1 | 32 | 512 | 1 | 45.9 | 11.33 | 87.5 | 16 |
| `Qwen/Qwen2.5-3B-Instruct` | decode | 1 | 32 | 512 | 2 | 73.9 | 11.45 | 171.6 | 32 |
| `Qwen/Qwen2.5-3B-Instruct` | decode | 1 | 32 | 512 | 4 | 84.5 | 12.99 | 282.1 | 52 |
| `Qwen/Qwen2.5-3B-Instruct` | decode | 1 | 32 | 512 | 8 | 126.5 | 12.10 | 596.9 | 112 |
