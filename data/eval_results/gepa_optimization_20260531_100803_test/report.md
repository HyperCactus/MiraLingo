# GEPA Optimization Results

**Date:** 2026-06-01 00:00 UTC  
**Optimizer:** GEPA (auto=light)  
**Train samples:** 3 (min 5 English words)  
**Num candidates:** 3 @ [0.1, 0.4, 0.8]  
**Context passages:** 3  
**Threads:** 24  
**Log dir:** data/eval_results/gepa_optimization_20260531_100803_test/gepa_logs  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | 10.0% (2/20) |
| Exact Match | 10.0% (2/20) |
| Avg Judge Score | 83.8/100 |

## Timing

| | |
|-|--|
| Compile time | 5526s (92.1 min) |
| Eval time | 3138s (52.3 min) |
| Avg per sample | 156.92s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
|   0 | ✗ |  95.0 | T=0.1 | this is the biggest house in our neighborhood → Hias se ha gwaga tam bi yata yubem. |
|   1 | ✗ |  93.0 | T=0.7 | you must do it as quickly as possible → Et yefe xer is igay hyayfway. |
|   2 | ✓ |  95.0 | T=0.3 | this house is not as big as mine → Hia tam voy se ge aga vyel atas. |
|   3 | ✗ |  70.0 | T=0.3 | how glad I am that you came → Hoy ivla at van et upa! |
|   4 | ✓ |  90.0 | T=0.1 | the whole world knows about you → Ha ayna mir te ayv et. |
|   5 | ✗ |  98.0 | T=0.7 | I think, therefore I am → at texe, husav at se |
|   6 | ✗ |  90.0 | T=0.3 | what a day this has been → Hyay! hia jub sa. |
|   7 | ✗ |  70.0 | T=0.1 | the baby is still sleeping → ha tudet tuje jey |
|   8 | ✗ |  98.0 | T=0.1 | I swim better than you → at pile ga fi vyel et |
|   9 | ✗ | 100.0 | T=0.1 | I am not your father → at voy se eta twed |
|  10 | ✗ |  40.0 | T=0.1 | it seems to me that → Tease at van |
|  11 | ✗ |  15.0 | T=0.1 | it does not bother me → is voy oboxe at |
|  12 | ✗ |  81.0 | T=0.7 | we would be going home but we would be happy here → yat su pea bu tam oy yat su iva him |
|  13 | ✗ | 100.0 | T=0.7 | we know that he or she will come and we will be happy → yat te van it upo ay yat so iva |
|  14 | ✗ | 100.0 | T=0.3 | we do not know where he or she went but we know where y → yat voy te duhom it pa oy yat te duhom e |
|  15 | ✗ |  45.0 | T=0.3 | do they know where we went and where you live → Du yit te hom yat pa ay hom et bese? |
|  16 | ✗ | 100.0 | T=0.1 | this teacher is good but that student is bad → hia tuxut se fia oy hua tixut se fua |
|  17 | ✗ |  95.0 | T=0.3 | even if I disagree you will support me → Gey ven at ovtexe, et bolo at. |
|  18 | ✗ | 100.0 | T=0.1 | you will never gain perfect happiness → et hyojob ako fika ivan |
|  19 | ✗ | 100.0 | T=0.7 | my house is bigger than yours → ata tam se ga aga vyel etas |

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
