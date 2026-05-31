#!/usr/bin/env python3
"""English→Mirad multi-candidate eval with full retrieval-context output.

Config: n_parallel=32, n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0
Output includes: judge scores + retrieved vocabulary + retrieved grammar rules.
"""

import os, sys, json, random, time, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

# ── Pre-warm: load embedding model once before workers start ───────────────
print("[warmup] Loading embedding model...")
t_warm = time.time()
from mirad_translator.semantic_lexicon import semantic_lookup_structured
_warm = semantic_lookup_structured("the quick brown fox", top_k_per_word=0, include_exact=True)
print(f"[warmup] Embedding model ready in {time.time()-t_warm:.1f}s. Pairs: {list(_warm['word_equivalents'].keys())}")

# ── Translator ──────────────────────────────────────────────────────────────
print("[setup] Building MultiCandidateTranslator (num_context_passages=3, top_k_per_word=0)...")
from mirad_translator.multi_candidate import MultiCandidateTranslator

shared_mc = MultiCandidateTranslator(
    num_candidates=3,
    temperatures=[0.1, 0.3, 0.7],
    num_context_passages=3,
    top_k_per_word=0,
)
shared_mc._get_lm(0.0)
print("[setup] Translator ready.")

# ── Load data ────────────────────────────────────────────────────────────────
with open("data/eval/train.json") as f:
    raw = json.load(f)
all_data = raw.get("pairs", raw) if isinstance(raw, dict) else raw

samples = []
for d in all_data:
    en = d.get("english", "") or d.get("source", "")
    mir = d.get("mirad", "") or d.get("target", "")
    if en:
        samples.append({"english": en, "mirad": mir, "id": d.get("id", "")})

rng = random.Random(20260526)
rng.shuffle(samples)
samples = samples[:100]
print(f"[data] {len(samples)} samples loaded (seed=20260526)")

# ── Retrieval helpers (local SQLite+ChromaDB — fast, no API calls) ──────────
def get_retrieval_context(english_text: str, top_k_per_word: int = 0, num_grammar_passages: int = 3):
    """Capture vocabulary + grammar retrieval for a given English text."""
    # Vocabulary: word equivalents + relevant words + back-translations
    vocab = semantic_lookup_structured(
        english_text,
        top_k_per_word=top_k_per_word,
        include_exact=True,
    )
    word_equivalents = vocab.get("word_equivalents", {})
    relevant_words = vocab.get("relevant_words", {})
    back_translations = vocab.get("back_translation", {})

    # Grammar rules: ChromaDB RAG retrieval
    from mirad_translator.translate import MiradContextRetrieve
    context_retriever = MiradContextRetrieve(k=num_grammar_passages)
    ctx_pred = context_retriever(query=english_text)
    grammar_passages = list(ctx_pred.passages)

    return {
        "word_equivalents": word_equivalents,    # exact English→Mirad dictionary matches
        "relevant_words": relevant_words,        # semantic neighbors (top_k_per_word > 0)
        "back_translations": back_translations,  # reverse lookups for context
        "grammar_passages": grammar_passages,     # top-k retrieved grammar-rule passages
        "num_grammar_passages": num_grammar_passages,
        "top_k_per_word": top_k_per_word,
    }

# ── Eval helper ──────────────────────────────────────────────────────────────
def eval_one(sample):
    # 1. Capture retrieval context (local — no API call)
    retrieval = get_retrieval_context(
        sample["english"],
        top_k_per_word=0,          # top_k_relevant_words=0 per user config
        num_grammar_passages=3,    # top_k_grammar_rules=3 per user config
    )

    # 2. Translate + judge (DeepInfra API calls)
    # Wrap in try/except so a single malformed API response doesn't kill the run
    try:
        pred = shared_mc(english_text=sample["english"])
    except Exception as exc:
        # Record the failure but don't crash the whole eval
        return {
            "id": sample.get("id", ""),
            "english_text": sample["english"],
            "gold": sample["mirad"],
            "pred": "",
            "exact_match": False,
            "normalized_match": False,
            "winner_index": -1,
            "total_score": 0.0,
            "rationale": f"ERROR: {type(exc).__name__}: {exc}",
            "candidates": [],
            "retrieval": retrieval,
            "error": f"{type(exc).__name__}: {exc}",
        }

    mirad_pred = pred.mirad_text

    def nmatch(a, b):
        a_n = re.sub(r"[^a-z0-9]", " ", a.lower())
        b_n = re.sub(r"[^a-z0-9]", " ", b.lower())
        return " ".join(a_n.split()) == " ".join(b_n.split())

    nm = bool(nmatch(mirad_pred, sample["mirad"]))
    em = bool(mirad_pred.strip() == sample["mirad"].strip())

    cand_summaries = []
    for c in (pred.candidates or []):
        j = c.get("judge", {})
        cand_summaries.append({
            "temp": c.get("temperature", 0),
            "mirad": c.get("mirad_text", ""),
            "total_score": j.get("total_score", 0),
            "grammar": j.get("grammar_score", 0),
            "morphology": j.get("morphology_score", 0),
            "vocab": j.get("vocabulary_score", 0),
            "bleed": j.get("english_bleed_score", 0),
            "complete": j.get("completeness_score", 0),
        })

    return {
        "id": sample.get("id", ""),
        "english_text": sample["english"],
        "gold": sample["mirad"],
        "pred": mirad_pred,
        "exact_match": em,
        "normalized_match": nm,
        "winner_index": getattr(pred, "winner_index", 0),
        "total_score": getattr(pred, "total_score", 0),
        "rationale": getattr(pred, "rationale", ""),
        "candidates": cand_summaries,
        # Full retrieval context (grammar rules + word equivalents + relevant words)
        "retrieval": retrieval,
    }

# ── Run eval ─────────────────────────────────────────────────────────────────
PARALLEL = 32
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = Path(f"data/eval_results/mc_eval_{ts}")
out_dir.mkdir(parents=True, exist_ok=True)

print(f"[eval] Starting: {len(samples)} samples, {PARALLEL} parallel workers")
t0 = time.time()
done = 0

with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
    futures = {ex.submit(eval_one, s): i for i, s in enumerate(samples)}
    examples = [None] * len(samples)
    for future in as_completed(futures):
        i = futures[future]
        examples[i] = future.result()
        done += 1
        if done % 10 == 0:
            elapsed = time.time() - t0
            remaining = (elapsed / done) * (len(samples) - done)
            print(f"  [{done}/{len(samples)}] elapsed={elapsed:.0f}s, ETA={remaining:.0f}s")

elapsed = time.time() - t0

# ── Metrics ──────────────────────────────────────────────────────────────────
nm_count = sum(1 for e in examples if e["normalized_match"])
em_count = sum(1 for e in examples if e["exact_match"])
error_count = sum(1 for e in examples if "error" in e)
n = len(examples)
valid_n = n - error_count
nm_rate = nm_count / valid_n
em_rate = em_count / valid_n
avg_score = sum(e["total_score"] for e in examples if "error" not in e) / max(1, valid_n)

with open("scripts/eval_config.yaml") as f:
    import yaml
    config = yaml.safe_load(f)
lm_model = config.get("model", {}).get("model", "deepseek-ai/DeepSeek-V4-Flash")

summary = {
    "config": {
        "num_candidates": 3,
        "temperatures": [0.1, 0.3, 0.7],
        "num_context_passages": 3,
        "top_k_per_word": 0,
        "parallel": PARALLEL,
        "random_seed": 20260526,
        "n_samples": n,
    },
    "metrics": {"normalized_match": nm_rate, "exact_match": em_rate, "avg_judge_score": avg_score},
    "counts": {"total": n, "normalized_match_correct": nm_count, "exact_match_correct": em_count, "errors": error_count},
    "timing": {"total_wall_s": round(elapsed, 1), "avg_per_sample_s": round(elapsed / n, 2)},
}

(out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))
(out_dir / "examples.json").write_text(json.dumps(examples, indent=2, ensure_ascii=False))

# ── Report ────────────────────────────────────────────────────────────────────
rows = []
for i, e in enumerate(examples):
    nm_sym = "✓" if e["normalized_match"] else "✗"
    if "error" in e:
        nm_sym = "ERR"
    we_count = len(e["retrieval"]["word_equivalents"])
    rw_count = len(e["retrieval"]["relevant_words"])
    gp_count = len(e["retrieval"]["grammar_passages"])
    winner_temp = "?"
    if e["candidates"]:
        winner_temp = e["candidates"][e["winner_index"]]["temp"]
    rows.append(
        f"| {i:3d} | {nm_sym} | {e['total_score']:5.1f} | T={winner_temp} "
        f"| WE:{we_count} RW:{rw_count} GP:{gp_count} | {e['english_text'][:50]} → {e.get('pred','')[:40]} |"
    )

# Sample retrieval detail for first 10 examples
detail_blocks = []
for i, e in enumerate(examples[:10]):
    we = e["retrieval"]["word_equivalents"]
    gp = e["retrieval"]["grammar_passages"]
    lines = [
        f"### Example {i}: {e['english_text'][:60]}",
        f"- **Pred:** {e['pred']}  **Gold:** {e['gold']}  **Score:** {e['total_score']:.0f}",
        f"- **Word equivalents ({len(we)}):** {dict(list(we.items())[:10])}",
        f"- **Grammar passages ({len(gp)}):**",
    ]
    for j, p in enumerate(gp[:3]):
        # Shorten for readability
        snippet = p[:200] + "..." if len(p) > 200 else p
        lines.append(f"  [{j+1}] {snippet}")
    lines.append("")
    detail_blocks.append("\n".join(lines))

report = f"""# Multi-Candidate Translation Eval (with Retrieval Context)

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Model:** {lm_model}
**Samples:** {n} (seed=20260526, from train.json)
**Direction:** English → Mirad
**Candidates:** 3 @ [0.1, 0.3, 0.7]
**Config:** n_parallel={PARALLEL}, n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0

## Metrics
| Metric | Value |
|--------|-------|
| Normalized Match | {nm_rate:.1%} ({nm_count}/{n - error_count}) |
| Exact Match | {em_rate:.1%} ({em_count}/{n - error_count}) |
| Avg Judge Score | {avg_score:.1f}/100 (excluding errors) |
| Errors | {error_count}/{n} |

## Timing
| | |
|-|--|
| Total wall time | {elapsed:.0f}s |
| Avg per sample | {elapsed/n:.1f}s |

## Results  (WE=word_equivalents, RW=relevant_words, GP=grammar_passages)
| # | NM | Judge | Temp | Context | Sample |
|---|----|-------|------|---------|--------|
{chr(10).join(rows)}

## Retrieval Detail (first 10 examples)

{detail_blocks[0] if detail_blocks else "(see examples.json for full retrieval context)"}
"""
(out_dir / "report.md").write_text(report)

print(f"\n{'='*60}")
print(f"RESULTS: n_parallel={PARALLEL}, n_candidates=3, k_grammar=3, k_relevant=0")
print(f"  Normalized Match: {nm_rate:.1%} ({nm_count}/{n})")
print(f"  Exact Match:      {em_rate:.1%} ({em_count}/{n})")
print(f"  Avg Judge Score:  {avg_score:.1f}/100")
print(f"  Wall time:        {elapsed:.0f}s")
print(f"  Output:           {out_dir}")
print(f"{'='*60}")