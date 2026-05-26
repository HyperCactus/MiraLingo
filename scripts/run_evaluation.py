#!/usr/bin/env python3
"""
Unified Mirad translation evaluation runner.

Loads evaluation config from YAML, builds the translator adapter, runs
parallel translations on the configured dataset, computes metrics, and
writes structured results to disk.

Usage:
  python scripts/run_evaluation.py --config scripts/eval_config.yaml

  # Or override config with CLI flags:
  python scripts/run_evaluation.py \
    --data data/eval/test.json \
    --direction en_to_mir \
    --n 30 \
    --parallel 8 \
    --model deepseek-ai/DeepSeek-V4-Flash

Config file (YAML) docs: scripts/eval_config.yaml
"""
from __future__ import annotations

import argparse, csv, json, math, os, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(_PROJECT_ROOT / "packages" / "translator" / "src"))

from translator_adapter import build_adapter, TranslationResult


# ── Argument parsing ─────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run a Mirad translation evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--config", type=Path, default=None,
                   help="Path to YAML config file. CLI flags override config values.")
    p.add_argument("--data", type=Path, default=None,
                   help="Path to JSON or CSV evaluation data.")
    p.add_argument("--direction", choices=["en_to_mir", "mir_to_en"], default=None,
                   help="Translation direction.")
    p.add_argument("--n", type=int, dest="n_samples", default=None,
                   help="Number of samples to evaluate (0 = all).")
    p.add_argument("--min-words", type=int, dest="min_english_words", default=None,
                   help="Minimum English words per sentence to include.")
    p.add_argument("--seed", type=int, dest="random_seed", default=None,
                   help="Random seed for sampling.")
    p.add_argument("--parallel", type=int, default=None,
                   help="Number of parallel translation calls.")
    p.add_argument("--model", type=str, default=None,
                   help="Override model name (e.g. deepseek-ai/DeepSeek-V4-Flash).")
    p.add_argument("--out-dir", type=Path, dest="out_dir", default=None,
                   help="Output directory for results.")
    p.add_argument("--metrics", type=str, nargs="+",
                   choices=["normalized_match", "word_overlap", "semantic_similarity"],
                   default=None,
                   help="Which metrics to compute.")
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite existing output directory.")
    p.add_argument("--translator-type", type=str, dest="translator_type", default=None,
                   help="Override translator type (default/compiled/custom path).")
    p.add_argument("--num-context-passages", type=int, dest="num_context_passages", default=None,
                   help="Number of grammar rules to retrieve (k).")
    p.add_argument("--top-k-per-word", type=int, dest="top_k_per_word", default=None,
                   help="Semantic lookup neighbors per word (top_k_per_word).")
    return p


def _merge_config(cfg: dict, args: argparse.Namespace) -> dict:
    """CLI args override config file values."""
    # Data
    if args.data is not None:
        cfg.setdefault("data", {})["path"] = str(args.data)
    if args.direction is not None:
        cfg.setdefault("data", {})["direction"] = args.direction
    if args.n_samples is not None:
        cfg.setdefault("data", {})["n_samples"] = args.n_samples
    if args.min_english_words is not None:
        cfg.setdefault("data", {})["min_english_words"] = args.min_english_words
    if args.random_seed is not None:
        cfg.setdefault("data", {})["random_seed"] = args.random_seed

    # Model
    if args.model is not None:
        cfg.setdefault("model", {})["model"] = args.model

    # Evaluation
    if args.parallel is not None:
        cfg.setdefault("evaluation", {})["parallel"] = args.parallel
    if args.metrics is not None:
        cfg.setdefault("evaluation", {})["metrics"] = args.metrics
    if args.overwrite:
        cfg.setdefault("output", {})["overwrite"] = True
    if args.out_dir is not None:
        cfg.setdefault("output", {})["out_dir"] = str(args.out_dir)
    if args.translator_type is not None:
        cfg.setdefault("translator", {})["type"] = args.translator_type
    if args.num_context_passages is not None:
        cfg.setdefault("translator", {})["num_context_passages"] = args.num_context_passages
    if args.top_k_per_word is not None:
        cfg.setdefault("translator", {})["top_k_per_word"] = args.top_k_per_word

    return cfg


def _load_config(path: Optional[Path]) -> dict:
    if path and path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


# ── Data loading ─────────────────────────────────────────────────────────────

@dataclass
class EvalSample:
    id: str
    source: str   # English for en_to_mir, Mirad for mir_to_en
    target: str   # Gold reference (Mirad for en_to_mir, English for mir_to_en)

    def norm(self, s: str) -> str:
        s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
        return re.sub(r"\s+", " ", s).strip().lower()


def load_data(config: dict) -> list[EvalSample]:
    """Load evaluation data from the configured path.

    Handles:
      - data/eval/*.json   (generic {id, source, target} or {id, english, mirad})
      - data/phrases/*.csv (english,mirad columns)
    """
    data_cfg = config.get("data", {})
    path = Path(data_cfg.get("path", "data/eval/test.json"))
    if not path.is_absolute():
        path = _PROJECT_ROOT / path

    direction = data_cfg.get("direction", "en_to_mir")
    min_words = data_cfg.get("min_english_words", 0)
    n_samples = data_cfg.get("n_samples", 0)
    seed      = data_cfg.get("random_seed", 20260526)

    if path.suffix == ".csv":
        rows = _load_csv(path, direction)
    else:
        rows = _load_json(path, direction)

    # Filter by minimum English words
    if min_words > 0:
        rows = [r for r in rows if len(r.source.strip().split()) >= min_words]

    # Random sample
    if 0 < n_samples < len(rows):
        random.seed(seed)
        rows = random.sample(rows, n_samples)

    return rows


def _load_json(path: Path, direction: str) -> list[EvalSample]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    # Accept both flat list and {"pairs": [...]} wrapper
    if isinstance(raw, dict):
        raw = raw.get("pairs", raw.get("data", raw))

    samples = []
    for item in raw:
        # Bidirectional format first: english + mirad (preferred)
        if "english" in item and "mirad" in item:
            source = item["english"] if direction == "en_to_mir" else item["mirad"]
            target = item["mirad"]   if direction == "en_to_mir" else item["english"]
        elif "source" in item and "target" in item:
            source = item["source"]
            target = item["target"]
        else:
            continue

        sid = item.get("id", f"unknown-{len(samples)}")
        samples.append(EvalSample(id=str(sid), source=str(source).strip(), target=str(target).strip()))

    return samples


def _load_csv(path: Path, direction: str) -> list[EvalSample]:
    samples = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            en = row.get("english", "").strip()
            mi = row.get("mirad", "").strip()
            if not en or not mi:
                continue
            source = en if direction == "en_to_mir" else mi
            target = mi if direction == "en_to_mir" else en
            samples.append(EvalSample(id=f"csv-{i:04d}", source=source, target=target))
    return samples


# ── Metrics ───────────────────────────────────────────────────────────────────

def normalized_match(gold: str, pred: str, norm_fn=staticmethod(lambda s: re.sub(r'[.,!?;:()"\'\[\]{}]', "", re.sub(r"\s+", " ", s)).strip().lower())) -> float:
    return 1.0 if norm_fn(gold) == norm_fn(pred) else 0.0


def word_overlap(gold: str, pred: str) -> tuple[float, float, float]:
    """Compute word-level precision, recall, and F1.

    Works for any language — compares word sets on the normalized strings.
    """
    def _words(s):
        s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
        return set(re.sub(r"\s+", " ", s).strip().lower().split())

    gw = _words(gold)
    pw = _words(pred)

    if not gw and not pw:
        return 1.0, 1.0, 1.0
    if not gw or not pw:
        return 0.0, 0.0, 0.0

    shared = gw & pw
    precision = len(shared) / len(pw) if pw else 0.0
    recall    = len(shared) / len(gw) if gw else 0.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


# ── Worker function ───────────────────────────────────────────────────────────

def _translate_worker(item: tuple[int, EvalSample], adapter) -> dict:
    idx, sample = item
    t0 = time.perf_counter()
    try:
        result = adapter.translate(sample.source)
        elapsed_ms = (time.perf_counter() - t0) * 1000
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return {
            "idx": idx,
            "id": sample.id,
            "source": sample.source,
            "gold": sample.target,
            "pred": "",
            "error": str(exc),
            "word_equivalents": {},
            "context_passages": [],
            "used_rule_ids": [],
            "elapsed_ms": round(elapsed_ms, 1),
            "scores": {},
        }

    return {
        "idx": idx,
        "id": sample.id,
        "source": sample.source,
        "gold": sample.target,
        "pred": result.translated_text,
        "error": None,
        "word_equivalents": result.word_equivalents,
        "context_passages": result.context_passages,
        "used_rule_ids": result.used_rule_ids,
        "elapsed_ms": round(elapsed_ms, 1),
        "scores": {},  # filled in after
    }


def _score_worker(result: dict, metrics: list[str], direction: str):
    gold = result["gold"]
    pred = result["pred"]
    scores = {}

    if "normalized_match" in metrics:
        norm_gold = re.sub(r'[.,!?;:()"\'\[\]{}]', "", re.sub(r"\s+", " ", gold)).strip().lower()
        norm_pred = re.sub(r'[.,!?;:()"\'\[\]{}]', "", re.sub(r"\s+", " ", pred)).strip().lower()
        scores["normalized_match"] = 1.0 if norm_gold == norm_pred else 0.0

    if "word_overlap" in metrics:
        p, r, f = word_overlap(gold, pred)
        scores["word_overlap_precision"] = round(p, 4)
        scores["word_overlap_recall"]    = round(r, 4)
        scores["word_overlap_f1"]        = round(f, 4)

    if "semantic_similarity" in metrics and direction == "mir_to_en":
        # Semantic similarity is only valid for Mir→En (English vs English)
        try:
            from mirad_translator.semantic_lexicon import _embedding_model
            model = _embedding_model()
            emb_g = model.encode([gold])
            emb_p = model.encode([pred])
            sim = float((emb_g[0] @ emb_p[0].T) / (math.sqrt(float(emb_g[0] @ emb_g[0].T)) * math.sqrt(float(emb_p[0] @ emb_p[0].T))))
            scores["semantic_similarity"] = round(sim, 4)
        except Exception:
            scores["semantic_similarity"] = None

    result["scores"] = scores
    return result


# ── Output writers ────────────────────────────────────────────────────────────

def _write_examples_json(results: list[dict], out_dir: Path, filename: str = "examples.json"):
    path = out_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return path


def _write_summary_json(meta: dict, results: list[dict], metrics: list[str], out_dir: Path) -> Path:
    scores_by_metric = {}
    for m in metrics:
        vals = [r["scores"].get(m, r["scores"].get(f"{m}_f1" if m == "word_overlap" else m)) for r in results if r["scores"].get(m) is not None or r["scores"].get(f"{m}_f1" if m == "word_overlap" else m) is not None]
        if vals:
            scores_by_metric[m] = sum(vals) / len(vals) if m != "word_overlap" else sum(vals) / len(vals)  # f1 is stored as word_overlap_f1

    # Rebuild cleanly
    score_clean = {}
    for m in metrics:
        if m == "word_overlap":
            score_clean["word_overlap_f1"] = round(sum(r["scores"].get("word_overlap_f1", 0) for r in results) / len(results), 4)
        else:
            vals = [r["scores"].get(m, 0) for r in results if r["scores"].get(m) is not None]
            if vals:
                score_clean[m] = round(sum(vals) / len(vals), 4)

    elapsed_vals = [r["elapsed_ms"] for r in results if r.get("elapsed_ms")]
    summary = {
        "metadata": meta,
        "metrics": score_clean,
        "timing": {
            "total_eval_ms": round(sum(elapsed_vals), 1),
            "avg_per_sample_ms": round(sum(elapsed_vals) / len(elapsed_vals), 1) if elapsed_vals else 0,
            "min_ms": round(min(elapsed_vals), 1) if elapsed_vals else 0,
            "max_ms": round(max(elapsed_vals), 1) if elapsed_vals else 0,
        },
        "counts": {
            "total": len(results),
            "errors": sum(1 for r in results if r.get("error")),
            "normalized_match_correct": sum(1 for r in results if r["scores"].get("normalized_match") == 1.0),
            "word_overlap_good": sum(1 for r in results if r["scores"].get("word_overlap_f1", 0) >= 0.7),
        },
    }
    path = out_dir / "run_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return path


def _write_report_md(meta: dict, results: list[dict], metrics: list[str], out_dir: Path) -> Path:
    score_clean = {}
    for m in metrics:
        if m == "word_overlap":
            score_clean["word_overlap_f1"] = round(sum(r["scores"].get("word_overlap_f1", 0) for r in results) / len(results), 4)
        else:
            vals = [r["scores"].get(m, 0) for r in results if r["scores"].get(m) is not None]
            if vals:
                score_clean[m] = round(sum(vals) / len(vals), 4)

    n_errors = sum(1 for r in results if r.get("error"))
    nm_correct = sum(1 for r in results if r["scores"].get("normalized_match") == 1.0)
    wo_good    = sum(1 for r in results if r["scores"].get("word_overlap_f1", 0) >= 0.7)

    lines = [
        f"# Translation Evaluation Report",
        f"",
        f"**Date:** {meta.get('timestamp', 'N/A')} | **Model:** {meta.get('model', 'N/A')}",
        f"**Direction:** {meta.get('direction', 'N/A')} | **Samples:** {len(results)}",
        f"**Data:** {meta.get('data_path', 'N/A')}",
        f"**Parallelism:** {meta.get('parallel', 'N/A')} workers",
        f"",
        f"## Metrics Summary",
        f"",
        f"| Metric | Score | Count |",
        f"|---|---|---|",
    ]

    if "normalized_match" in metrics:
        lines.append(f"| Normalized Match | {score_clean.get('normalized_match', 0):.1%} | {nm_correct}/{len(results)} |")
    if "word_overlap" in metrics:
        lines.append(f"| Word Overlap F1 | {score_clean.get('word_overlap_f1', 0):.1%} | {wo_good}/{len(results)} (≥0.7) |")
    if "semantic_similarity" in metrics:
        lines.append(f"| Semantic Similarity | {score_clean.get('semantic_similarity', 0):.4f} | — |")
    lines.append(f"| Avg Time/Sample | {meta.get('avg_time_ms', 0):.0f}ms | — |")
    lines.append(f"")

    if n_errors > 0:
        lines.append(f"## Errors ({n_errors})")
        for r in results:
            if r.get("error"):
                lines.append(f"- **[{r['id']}]** `{r['source'][:60]}`")
                lines.append(f"  - Error: {r['error']}")
        lines.append(f"")

    lines += [
        f"## All Results",
        f"",
        f"| # | Source | Gold | Predicted | Score | Time |",
        f"|---|---|---|---|---|---|",
    ]
    for r in sorted(results, key=lambda x: x["idx"]):
        nm = r["scores"].get("normalized_match", 0)
        flag = "✓" if nm == 1.0 else "✗"
        lines.append(
            f"| {r['idx']} | {r['source'][:40]} | {r['gold'][:25]} | "
            f"{r['pred'][:25]} | {flag} | {r['elapsed_ms']:.0f}ms |"
        )

    path = out_dir / "report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = _build_parser()
    args = parser.parse_args()

    # Load config
    raw_cfg  = _load_config(args.config)
    config   = _merge_config(raw_cfg, args)

    # Resolve output dir
    out_cfg = config.get("output", {})
    if out_cfg.get("out_dir"):
        out_dir = Path(out_cfg["out_dir"])
    else:
        config_name = args.config.stem if args.config else "cli"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = _PROJECT_ROOT / "data" / "eval_results" / f"{config_name}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if out_dir.exists() and any(out_dir.iterdir()) and not out_cfg.get("overwrite"):
        print(f"ERROR: Output directory {out_dir} already has files. Use --overwrite to replace.")
        sys.exit(1)

    # Load data
    print(f"Loading data from {config.get('data', {}).get('path', 'N/A')} ...")
    samples = load_data(config)
    if not samples:
        print("ERROR: No samples loaded. Check --data, --direction, and --min-words.")
        sys.exit(1)
    print(f"  {len(samples)} samples loaded")

    # Build adapter
    print("Building translator adapter ...")
    adapter = build_adapter(config)
    print(f"  Direction: {adapter.direction}")

    # Eval settings
    eval_cfg  = config.get("evaluation", {})
    metrics   = eval_cfg.get("metrics", ["normalized_match", "word_overlap"])
    parallel  = eval_cfg.get("parallel", 8)
    direction = adapter.direction

    print(f"Running evaluation ({parallel} parallel) ...")
    t_eval_start = time.perf_counter()

    # Phase 1: Translate all samples
    results = []
    done = 0
    items = list(enumerate(samples))
    with ThreadPoolExecutor(max_workers=parallel) as ex:
        futures = {ex.submit(_translate_worker, item, adapter): item for item in items}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            done += 1
            flag = "✓" if r["error"] is None and r["scores"].get("normalized_match") == 1.0 else "✗"
            elapsed = r.get("elapsed_ms", 0)
            print(f"  [{done:3d}/{len(samples)}] {flag} {elapsed:6.0f}ms  {r['source'][:50]}")

    # Phase 2: Score all results
    for r in results:
        _score_worker(r, metrics, direction)

    t_eval = (time.perf_counter() - t_eval_start) * 1000
    adapter.close()

    # Aggregate
    total_ms = sum(r["elapsed_ms"] for r in results)
    meta = {
        "timestamp": datetime.now().isoformat(),
        "model": config.get("model", {}).get("model", "unknown"),
        "direction": direction,
        "data_path": config.get("data", {}).get("path", "N/A"),
        "parallel": parallel,
        "n_samples": len(samples),
        "random_seed": config.get("data", {}).get("random_seed", 0),
        "min_english_words": config.get("data", {}).get("min_english_words", 0),
        "config_file": str(args.config) if args.config else None,
        "eval_duration_ms": round(t_eval, 1),
        "avg_time_ms": round(total_ms / len(results), 1) if results else 0,
    }

    # Write outputs
    print(f"\nSaving results to {out_dir} ...")
    _write_examples_json(results, out_dir)
    _write_summary_json(meta, results, metrics, out_dir)
    _write_report_md(meta, results, metrics, out_dir)

    # Print summary
    print(f"\nDone in {t_eval/1000:.1f}s")
    for m in metrics:
        if m == "word_overlap":
            avg = sum(r["scores"].get("word_overlap_f1", 0) for r in results) / len(results)
            good = sum(1 for r in results if r["scores"].get("word_overlap_f1", 0) >= 0.7)
            print(f"  word_overlap_f1: {avg:.1%}  (≥0.7: {good}/{len(results)})")
        else:
            vals = [r["scores"].get(m, 0) for r in results if r["scores"].get(m) is not None]
            if vals:
                avg = sum(vals) / len(vals)
                correct = sum(1 for v in vals if v == 1.0)
                print(f"  {m}: {avg:.1%}  ({correct}/{len(results)})")

    print(f"\nResults → {out_dir}")
    print(f"  examples.json   → per-example data with context")
    print(f"  run_summary.json → aggregated metrics + timing")
    print(f"  report.md       → human-readable report")


if __name__ == "__main__":
    main()