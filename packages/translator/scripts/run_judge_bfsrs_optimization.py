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
    SplitJudgeModule,
    example_to_dspy,
    judge_metric,
    load_curated_judge_dataset,
    make_deepinfra_lm,
    parse_judge_json,
)

DEFAULT_DATASET = PROJECT_ROOT / 'data' / 'eval' / 'judge_curated_100_en_to_mir.json'
DEFAULT_OUT_BASE = PROJECT_ROOT / 'data' / 'eval_results'


def score_examples(module: dspy.Module, devset: list[dspy.Example]) -> list[dict]:
    rows = []
    for ex in devset:
        pred = module(
            source_text=ex.source_text,
            candidate_payload_json=ex.candidate_payload_json,
        )
        candidate_ids = [row['candidate_id'] for row in json.loads(ex.candidate_payload_json)]
        gold = parse_judge_json(ex.judge_json, candidate_ids)
        predicted = parse_judge_json(getattr(pred, 'judge_json', ''), candidate_ids)
        rows.append({
            'example_id': ex.example_id,
            'source_text': ex.source_text,
            'expected_text': ex.expected_text,
            'gold': gold,
            'predicted': predicted,
            'metric': judge_metric(ex, pred),
            'winner_correct': gold['selected_candidate_id'] == predicted['selected_candidate_id'],
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description='Optimize split judge with BootstrapFewShotWithRandomSearch')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--out-dir', type=Path, default=None)
    parser.add_argument('--train-size', type=int, default=80)
    parser.add_argument('--val-size', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num-candidate-programs', type=int, default=6)
    parser.add_argument('--max-bootstrapped-demos', type=int, default=6)
    parser.add_argument('--max-labeled-demos', type=int, default=12)
    parser.add_argument('--max-rounds', type=int, default=1)
    parser.add_argument('--num-threads', type=int, default=8)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    data = load_curated_judge_dataset(args.dataset)
    if len(data) < args.train_size + args.val_size:
        raise ValueError('dataset smaller than requested train+val sizes')

    import random
    rng = random.Random(args.seed)
    data = list(data)
    rng.shuffle(data)
    train_raw = data[: args.train_size]
    val_raw = data[args.train_size: args.train_size + args.val_size]
    trainset = [example_to_dspy(x) for x in train_raw]
    valset = [example_to_dspy(x) for x in val_raw]

    if args.out_dir:
        out_dir = args.out_dir
    else:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out_dir = DEFAULT_OUT_BASE / f'judge_bfsrs_{stamp}'
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        summary = {
            'dataset': str(args.dataset),
            'train_size': len(trainset),
            'val_size': len(valset),
            'out_dir': str(out_dir),
            'status': 'dry-run',
        }
        (out_dir / 'run_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(json.dumps(summary, indent=2))
        return

    lm = make_deepinfra_lm(temperature=0.0, max_tokens=2048)
    dspy.settings.configure(lm=lm)

    student = SplitJudgeModule()
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=judge_metric,
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

    evaluator = Evaluate(devset=valset, metric=judge_metric, num_threads=args.num_threads, display_progress=True, display_table=0)
    eval_result = evaluator(compiled)
    details = score_examples(compiled, valset)
    winner_accuracy = sum(1 for row in details if row['winner_correct']) / max(1, len(details))

    compiled_dir = out_dir / 'compiled_program'
    save_compiled_program(compiled, str(compiled_dir))

    summary = {
        'dataset': str(args.dataset),
        'train_size': len(trainset),
        'val_size': len(valset),
        'compile_time_s': round(compile_s, 2),
        'judge_metric': getattr(eval_result, 'score', eval_result),
        'winner_accuracy': round(winner_accuracy, 4),
        'compiled_program_dir': str(compiled_dir),
        'config': {
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
            '# Judge BFSRS Optimization',
            '',
            f"- Dataset: `{args.dataset}`",
            f"- Train size: {len(trainset)}",
            f"- Val size: {len(valset)}",
            f"- Judge metric: {summary['judge_metric']}",
            f"- Winner accuracy: {winner_accuracy:.1%}",
            f"- Compiled program: `{compiled_dir}`",
        ]),
        encoding='utf-8',
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
