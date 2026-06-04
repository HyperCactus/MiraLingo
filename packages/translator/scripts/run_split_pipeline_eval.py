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

from mirad_translator.split_pipeline import (
    exact_match_metric,
    generate_candidates_with_module,
    load_generator_pairs,
    make_deepinfra_lm,
    normalized_match_metric,
    pick_best_with_judge,
)

DEFAULT_TEST = PROJECT_ROOT / 'data' / 'eval' / 'test.json'
DEFAULT_OUT_BASE = PROJECT_ROOT / 'data' / 'eval_results'


def main() -> None:
    parser = argparse.ArgumentParser(description='Evaluate split generator + judge pipeline')
    parser.add_argument('--generator-program', type=Path, required=True)
    parser.add_argument('--judge-program', type=Path, required=True)
    parser.add_argument('--test', type=Path, default=DEFAULT_TEST)
    parser.add_argument('--max-examples', type=int, default=20)
    parser.add_argument('--candidate-count', type=int, default=3)
    parser.add_argument('--temperatures', type=float, nargs='+', default=[0.1, 0.4, 0.8])
    parser.add_argument('--num-threads', type=int, default=24)
    parser.add_argument('--out-dir', type=Path, default=None)
    args = parser.parse_args()

    if args.out_dir:
        out_dir = args.out_dir
    else:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out_dir = DEFAULT_OUT_BASE / f'split_pipeline_eval_{stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)

    dspy.settings.configure(lm=make_deepinfra_lm(temperature=0.0, max_tokens=4096))
    generator = dspy.load(str(args.generator_program), allow_pickle=True)
    judge = dspy.load(str(args.judge_program), allow_pickle=True)
    evalset = load_generator_pairs(args.test, max_samples=args.max_examples, seed=42)

    class SplitPipeline(dspy.Module):
        def __init__(self, generator: dspy.Module, judge: dspy.Module, temperatures: list[float], candidate_count: int):
            super().__init__()
            self.generator = generator
            self.judge = judge
            self.temperatures = list(temperatures)
            self.candidate_count = candidate_count

        def forward(self, *, english_text: str) -> dspy.Prediction:
            candidates = generate_candidates_with_module(
                self.generator,
                english_text,
                self.temperatures,
                self.candidate_count,
            )
            judged = pick_best_with_judge(self.judge, english_text, '', candidates)
            best = judged['best_candidate']
            return dspy.Prediction(
                mirad_text=best['candidate_text'],
                judge=judged['judge'],
                candidates=judged['ranked_candidates'],
            )

    evaluator = dspy.Evaluate(
        devset=evalset,
        metric=normalized_match_metric,
        num_threads=args.num_threads,
        display_progress=True,
    )
    t0 = time.time()
    evaluation = evaluator(SplitPipeline(generator, judge, args.temperatures, args.candidate_count))
    elapsed = time.time() - t0

    results = []
    for ex, pred, _score in evaluation.results:
        results.append({
            'english_text': ex.english_text,
            'gold_mirad': ex.mirad_text,
            'pred_mirad': getattr(pred, 'mirad_text', ''),
            'normalized_match': normalized_match_metric(ex, pred),
            'exact_match': exact_match_metric(ex, pred),
            'judge': getattr(pred, 'judge', {}),
            'candidates': getattr(pred, 'candidates', []),
        })

    nm = sum(r['normalized_match'] for r in results) / max(1, len(results))
    em = sum(r['exact_match'] for r in results) / max(1, len(results))
    summary = {
        'generator_program': str(args.generator_program),
        'judge_program': str(args.judge_program),
        'test': str(args.test),
        'examples': len(results),
        'normalized_match': nm,
        'exact_match': em,
        'wall_time_s': round(elapsed, 2),
        'candidate_count': args.candidate_count,
        'temperatures': args.temperatures,
        'num_threads': args.num_threads,
    }
    (out_dir / 'run_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    (out_dir / 'examples.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    (out_dir / 'report.md').write_text(
        '\n'.join([
            '# Split Pipeline Eval',
            '',
            f"- Examples: {len(results)}",
            f"- Normalized match: {nm:.1%}",
            f"- Exact match: {em:.1%}",
            f"- Wall time: {elapsed:.1f}s",
        ]),
        encoding='utf-8',
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
