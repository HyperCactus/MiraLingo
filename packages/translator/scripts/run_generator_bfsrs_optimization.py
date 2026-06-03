#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSLATOR_SRC = PROJECT_ROOT / 'packages' / 'translator' / 'src'
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))

import dspy
from dspy import BootstrapFewShotWithRandomSearch, Evaluate

from mirad_translator.evaluate import save_compiled_program
from mirad_translator.split_pipeline import (
    build_generator_module,
    exact_match_metric,
    load_generator_pairs,
    make_deepinfra_lm,
    normalized_match_metric,
)

DEFAULT_TRAIN = PROJECT_ROOT / 'data' / 'eval' / 'train.json'
DEFAULT_VAL = PROJECT_ROOT / 'data' / 'eval' / 'val.json'
DEFAULT_OUT_BASE = PROJECT_ROOT / 'data' / 'eval_results'


def main() -> None:
    parser = argparse.ArgumentParser(description='Optimize English→Mirad generator with BootstrapFewShotWithRandomSearch')
    parser.add_argument('--train', type=Path, default=DEFAULT_TRAIN)
    parser.add_argument('--val', type=Path, default=DEFAULT_VAL)
    parser.add_argument('--bootstrap-n', type=int, default=80)
    parser.add_argument('--val-n', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num-context-passages', type=int, default=3)
    parser.add_argument('--top-k-per-word', type=int, default=2)
    parser.add_argument('--num-candidate-programs', type=int, default=6)
    parser.add_argument('--max-bootstrapped-demos', type=int, default=6)
    parser.add_argument('--max-labeled-demos', type=int, default=12)
    parser.add_argument('--max-rounds', type=int, default=1)
    parser.add_argument('--num-threads', type=int, default=8)
    parser.add_argument('--out-dir', type=Path, default=None)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    trainset = load_generator_pairs(args.train, max_samples=args.bootstrap_n, seed=args.seed)
    valset = load_generator_pairs(args.val, max_samples=args.val_n, seed=args.seed + 1)

    if args.out_dir:
        out_dir = args.out_dir
    else:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out_dir = DEFAULT_OUT_BASE / f'generator_bfsrs_{stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        summary = {
            'train_size': len(trainset),
            'val_size': len(valset),
            'out_dir': str(out_dir),
            'status': 'dry-run',
        }
        (out_dir / 'run_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(json.dumps(summary, indent=2))
        return

    lm = make_deepinfra_lm(temperature=0.0, max_tokens=4096)
    dspy.settings.configure(lm=lm)

    student = build_generator_module(
        num_context_passages=args.num_context_passages,
        top_k_per_word=args.top_k_per_word,
    )
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=normalized_match_metric,
        max_bootstrapped_demos=args.max_bootstrapped_demos,
        max_labeled_demos=args.max_labeled_demos,
        max_rounds=args.max_rounds,
        num_candidate_programs=args.num_candidate_programs,
        num_threads=args.num_threads,
        max_errors=5,
    )

    t0 = time.time()
    compiled = optimizer.compile(student=student, trainset=trainset, valset=valset)
    compile_s = time.time() - t0

    norm_eval = Evaluate(devset=valset, metric=normalized_match_metric, num_threads=args.num_threads, display_progress=True, display_table=0)
    exact_eval = Evaluate(devset=valset, metric=exact_match_metric, num_threads=args.num_threads, display_progress=False, display_table=0)
    norm_result = norm_eval(compiled)
    exact_result = exact_eval(compiled)

    details = []
    for ex in valset:
        pred = compiled(english_text=ex.english_text)
        details.append({
            'english_text': ex.english_text,
            'gold_mirad': ex.mirad_text,
            'pred_mirad': getattr(pred, 'mirad_text', ''),
            'normalized_match': normalized_match_metric(ex, pred),
            'exact_match': exact_match_metric(ex, pred),
        })

    compiled_dir = out_dir / 'compiled_program'
    save_compiled_program(compiled, str(compiled_dir))

    summary = {
        'train_size': len(trainset),
        'val_size': len(valset),
        'compile_time_s': round(compile_s, 2),
        'normalized_match': getattr(norm_result, 'score', norm_result),
        'exact_match': getattr(exact_result, 'score', exact_result),
        'compiled_program_dir': str(compiled_dir),
        'config': {
            'num_context_passages': args.num_context_passages,
            'top_k_per_word': args.top_k_per_word,
            'num_candidate_programs': args.num_candidate_programs,
            'max_bootstrapped_demos': args.max_bootstrapped_demos,
            'max_labeled_demos': args.max_labeled_demos,
            'max_rounds': args.max_rounds,
            'num_threads': args.num_threads,
        },
    }
    (out_dir / 'run_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    (out_dir / 'examples.json').write_text(json.dumps(details, indent=2, ensure_ascii=False), encoding='utf-8')
    (out_dir / 'report.md').write_text(
        '\n'.join([
            '# Generator BFSRS Optimization',
            '',
            f"- Train size: {len(trainset)}",
            f"- Val size: {len(valset)}",
            f"- Normalized match: {summary['normalized_match']}",
            f"- Exact match: {summary['exact_match']}",
            f"- Compiled program: `{compiled_dir}`",
        ]),
        encoding='utf-8',
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
