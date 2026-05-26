# top_k_per_word Sweep Results

Run at: 2026-05-26T17:39:27.215955
Data: data/eval/train.json | n=30 | seed=20260526
k (num_context_passages): locked at 3 (from prior sweep)


| top_k | direction | accuracy | ms/sample | n |
|-------|-----------|----------|-----------|---|
| 0 | en_to_mir | 13.3% | 17365.5 | 30 |
| 0 | mir_to_en | 40.0% | 15936.7 | 30 |
| 3 | en_to_mir | 10.0% | 34958.7 | 30 |
| 3 | mir_to_en | 40.0% | 17341.0 | 30 |
| 5 | en_to_mir | 10.0% | 15502.1 | 30 |
| 5 | mir_to_en | 40.0% | 15787.3 | 30 |
| 8 | en_to_mir | 10.0% | 16701.9 | 30 |
| 8 | mir_to_en | 36.7% | 16570.2 | 30 |
