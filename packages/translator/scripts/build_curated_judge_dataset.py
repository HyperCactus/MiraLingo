#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSLATOR_SRC = PROJECT_ROOT / 'packages' / 'translator' / 'src'
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))

from mirad_translator.split_pipeline import assess_candidate, infer_taxonomy_focus, strip_punct, tokenize

DEFAULT_SOURCES = [
    PROJECT_ROOT / 'data' / 'eval_results' / 'mc_eval_20260528_165529' / 'examples.json',
    PROJECT_ROOT / 'data' / 'eval_results' / 'mipro_full_660' / 'test_set_examples.json',
]
DEFAULT_OUT = PROJECT_ROOT / 'data' / 'eval' / 'judge_curated_100_en_to_mir.json'
DEFAULT_SMOKE_OUT = PROJECT_ROOT / 'data' / 'eval' / 'judge_curated_smoke_en_to_mir.json'

OVERRIDES = {
    'pair-0084': {'winner_text_contains': 'hua aot', 'bucket': 'likely_valid_alternative', 'score': 0.9, 'notes': 'Uses an analytic “that person” construction for the demonstrative subject and preserves the intended referent.'},
    'pair-0451': {'winner_text_contains': 'Upu eku bay yat', 'bucket': 'likely_valid_alternative', 'score': 0.9, 'notes': 'Uses imperative morphology and keeps the request directed at the speaker group.'},
    'pair-0505': {'winner_text_contains': 'Dalu yugay', 'bucket': 'likely_valid_alternative', 'score': 0.88, 'notes': 'Keeps the command and adverbial manner; casing/punctuation are the only surface concern.'},
    'pair-0561': {'winner_text_contains': 'Fia av et', 'bucket': 'likely_valid_alternative', 'score': 0.86, 'notes': 'Conveys the praise formula with “good” directed toward the addressee.'},
    'pair-0832': {'winner_text_contains': 'at se him', 'bucket': 'likely_valid_alternative', 'score': 0.89, 'notes': 'Preserves first-person present location with a plausible here-clause form.'},
    'pair-0180': {'winner_text_contains': 'suyu', 'bucket': 'major_error', 'score': 0.22, 'notes': 'Over-generates hypothetical/copular morphology, making the verb form incompatible with the source.'},
    'pair-0250': {'winner_text_contains': 'eyt po', 'bucket': 'major_error', 'score': 0.18, 'notes': 'Uses the wrong plural pronoun form, so the subject is not the source “you all”.'},
    'pair-0742': {'winner_text_contains': 'Eyt voy pue', 'bucket': 'major_error', 'score': 0.16, 'notes': 'Uses the wrong plural pronoun and a bad verb form, despite preserving negation.'},
    'pair-0194': {'winner_text_contains': 'xero', 'bucket': 'major_error', 'score': 0.2, 'notes': 'Uses an incorrect future-like verb form, so tense/aspect is not reliable.'},
    'pair-0209': {'winner_text_contains': 'it ey it upya', 'bucket': 'completely_wrong', 'score': 0.02, 'notes': 'Duplicates the subject around “or” and uses a perfect-like form where the source only needs simple coming.'},
}

TARGET_COUNTS = {
    'exact_match': 20,
    'punctuation_variant': 10,
    'likely_valid_alternative': 25,
    'minor_error': 25,
    'major_error': 15,
    'completely_wrong': 5,
}

GOOD_TOKEN_HINTS = {
    'se': 'includes the required copula for a predicate adjective/noun',
    'voy': 'preserves negation',
    'ay': 'preserves the additive conjunction',
    'oy': 'preserves the contrastive “but” relation',
    'ven': 'preserves the if/whether clause marker',
    'van': 'preserves the that/so-that clause marker',
    'ha': 'keeps the definite article where the source has a definite noun phrase',
}

BAD_TOKEN_HINTS = {
    'se': 'missing copula between subject and predicate',
    'voy': 'missing source negation',
    'ay': 'missing additive conjunction',
    'oy': 'missing contrastive “but” relation',
    'ven': 'missing if/whether clause marker',
    'van': 'missing that/so-that clause marker',
    'ha': 'drops a definite article from a definite noun phrase',
}


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        raise ValueError(f'{path} must be a list of examples')
    return payload


def normalize_candidates(row: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for i, cand in enumerate(row.get('candidates') or [], 1):
        text = cand.get('mirad') or cand.get('prediction') or cand.get('candidate_text') or ''
        if not text:
            continue
        out.append({
            'candidate_id': cand.get('candidate_id') or f'cand-{i}',
            'candidate_text': str(text).strip(),
            'source': row.get('id', 'unknown'),
            'temperature': cand.get('temp') or cand.get('temperature'),
            'raw_candidate': cand,
        })
    dedup = []
    seen = set()
    for c in out:
        key = strip_punct(c['candidate_text'])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(c)
    return dedup


def _bucket_from_score(score: float) -> str:
    if score >= 0.97:
        return 'exact_match'
    if score >= 0.93:
        return 'punctuation_variant'
    if score >= 0.82:
        return 'likely_valid_alternative'
    if score >= 0.58:
        return 'minor_error'
    if score >= 0.3:
        return 'major_error'
    return 'completely_wrong'


def apply_override(example_id: str, candidates: list[dict[str, Any]], labels: dict[str, dict[str, Any]]) -> None:
    override = OVERRIDES.get(example_id)
    if not override:
        return
    needle = override['winner_text_contains'].lower()
    for c in candidates:
        if needle in c['candidate_text'].lower():
            label = labels[c['candidate_id']]
            label['aggregate_score'] = override['score']
            label['label'] = override['bucket']
            label['notes'] = override['notes']
            break


def _candidate_specific_rationale(source_text: str, expected_text: str, candidate_text: str, score: float) -> str:
    gold_tokens = tokenize(expected_text)
    cand_tokens = tokenize(candidate_text)
    gold_set = set(gold_tokens)
    cand_set = set(cand_tokens)
    missing = [tok for tok in gold_tokens if tok not in cand_set]
    extra = [tok for tok in cand_tokens if tok not in gold_set]
    same_norm = strip_punct(expected_text) == strip_punct(candidate_text)
    exact_surface = candidate_text.strip() == expected_text.strip()

    if exact_surface:
        positives = [hint for token, hint in GOOD_TOKEN_HINTS.items() if token in gold_set][:2]
        if positives:
            return 'Strong candidate: ' + '; '.join(positives) + ', while preserving the source meaning.'
        return 'Strong candidate: preserves the source meaning with grammatical Mirad word order and no added or missing content.'

    if same_norm:
        return 'Semantically and grammatically strong; only capitalization or sentence-final punctuation differs, which should not outweigh meaning.'

    issues: list[str] = []
    for token in missing:
        if token in BAD_TOKEN_HINTS and BAD_TOKEN_HINTS[token] not in issues:
            issues.append(BAD_TOKEN_HINTS[token])
    if ' is ' in f' {source_text.lower()} ' or ' are ' in f' {source_text.lower()} ' or ' am ' in f' {source_text.lower()} ':
        if 'se' in gold_set and 'se' not in cand_set and 'missing copula between subject and predicate' not in issues:
            issues.append('missing copula between subject and predicate')
    if len(cand_tokens) >= 2 and len(gold_tokens) >= 2 and cand_tokens != gold_tokens and cand_set == gold_set:
        issues.append('uses the right words but in an unnatural or rule-violating order')
    if extra:
        issues.append('adds unsupported token(s): ' + ', '.join(extra[:3]))
    if missing and not issues:
        issues.append('omits required token(s): ' + ', '.join(missing[:3]))
    if not issues:
        issues.append('keeps some lexical overlap but has material word choice or morphology drift')

    if score >= 0.82:
        return 'Acceptable candidate: ' + '; '.join(issues[:2]) + ', but core source meaning remains recoverable.'
    if score >= 0.58:
        return 'Partial candidate: ' + '; '.join(issues[:3]) + '.'
    if score >= 0.3:
        return 'Weak candidate: ' + '; '.join(issues[:3]) + ', causing major loss of source meaning or grammar.'
    return 'Bad candidate: ' + '; '.join(issues[:3]) + ', so it should be ranked last or near last.'


def _winner_rationale(source_text: str, expected_text: str, winner: dict[str, Any], labels: dict[str, dict[str, Any]], ranked: list[dict[str, Any]]) -> str:
    winner_label = labels[winner['candidate_id']]
    winner_reason = _candidate_specific_rationale(source_text, expected_text, winner['candidate_text'], winner_label['aggregate_score'])
    if len(ranked) > 1:
        runner = ranked[1]
        runner_label = labels[runner['candidate_id']]
        if winner_label['aggregate_score'] - runner_label['aggregate_score'] >= 0.1:
            runner_reason = _candidate_specific_rationale(source_text, expected_text, runner['candidate_text'], runner_label['aggregate_score'])
            return f"{winner_reason} It beats {runner['candidate_id']} because {runner_reason[0].lower() + runner_reason[1:]}"
    return winner_reason


def _candidate_payload(candidates: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{'candidate_id': c['candidate_id'], 'candidate_text': c['candidate_text']} for c in candidates]


def _criteria_scores(score: float) -> dict[str, float]:
    if score >= 0.93:
        return {'semantic_fidelity': 0.98, 'grammar': 0.96, 'morphology': 0.96, 'fluency': 0.95}
    if score >= 0.82:
        return {'semantic_fidelity': 0.9, 'grammar': 0.86, 'morphology': 0.84, 'fluency': 0.86}
    if score >= 0.58:
        return {'semantic_fidelity': 0.72, 'grammar': 0.62, 'morphology': 0.58, 'fluency': 0.68}
    if score >= 0.3:
        return {'semantic_fidelity': 0.45, 'grammar': 0.38, 'morphology': 0.34, 'fluency': 0.42}
    return {'semantic_fidelity': 0.18, 'grammar': 0.16, 'morphology': 0.12, 'fluency': 0.18}


def curate_examples(source_paths: list[Path], total_examples: int) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {key: [] for key in TARGET_COUNTS}
    seen_ids: set[str] = set()
    for source_path in source_paths:
        for row in load_rows(source_path):
            example_id = str(row.get('id', ''))
            if not example_id or example_id in seen_ids:
                continue
            candidates = normalize_candidates(row)
            if len(candidates) < 2:
                continue
            source_text = row.get('english_text') or row.get('input') or ''
            expected_text = row.get('gold') or row.get('expected') or ''
            if not source_text or not expected_text:
                continue
            seen_ids.add(example_id)
            labels: dict[str, dict[str, Any]] = {}
            for candidate in candidates:
                assessment = assess_candidate(source_text=source_text, expected_text=expected_text, candidate_text=candidate['candidate_text'])
                labels[candidate['candidate_id']] = {
                    'aggregate_score': assessment.aggregate_score,
                    'label': assessment.label,
                    'notes': _candidate_specific_rationale(source_text, expected_text, candidate['candidate_text'], assessment.aggregate_score),
                    'criteria_scores': assessment.criteria_scores,
                    'error_tags': assessment.error_tags,
                }
            apply_override(example_id, candidates, labels)
            for candidate in candidates:
                labels[candidate['candidate_id']]['label'] = _bucket_from_score(float(labels[candidate['candidate_id']]['aggregate_score']))
                labels[candidate['candidate_id']]['criteria_scores'] = _criteria_scores(float(labels[candidate['candidate_id']]['aggregate_score']))
            ranked = sorted(candidates, key=lambda item: (-labels[item['candidate_id']]['aggregate_score'], item['candidate_id']))
            for rank, candidate in enumerate(ranked, 1):
                label = labels[candidate['candidate_id']]
                label['rank'] = rank
                label['is_correct'] = rank == 1 and label['aggregate_score'] >= 0.82
            winner = ranked[0]
            winner_label = labels[winner['candidate_id']]
            bucket = winner_label['label']
            if bucket not in buckets:
                continue
            rationale = _winner_rationale(source_text, expected_text, winner, labels, ranked)
            winner_label['notes'] = rationale
            taxonomy = sorted(set(infer_taxonomy_focus(source_text, expected_text, winner['candidate_text']) + winner_label['error_tags']))
            judge_json = {
                'selected_candidate_id': winner['candidate_id'],
                'candidate_scores': {c['candidate_id']: round(float(labels[c['candidate_id']]['aggregate_score']), 2) for c in candidates},
                'ranking': [c['candidate_id'] for c in ranked],
                'confidence': round(min(0.99, max(0.55, float(winner_label['aggregate_score']) + 0.08)), 2),
                'rationale': rationale,
            }
            curated = {
                'example_id': example_id,
                'dspy_inputs': ['source_text', 'candidate_payload_json'],
                'direction': 'en_to_mir',
                'source_text': source_text,
                'candidate_payload_json': json.dumps(_candidate_payload(candidates), ensure_ascii=False),
                'judge_json': json.dumps(judge_json, ensure_ascii=False, sort_keys=True),
                'rationale': rationale,
                'expected_text': expected_text,
                'source_reference': str(source_path.relative_to(PROJECT_ROOT)),
                'taxonomy_focus': taxonomy,
                'candidate_labels': [
                    {
                        'candidate_id': c['candidate_id'],
                        'candidate_text': c['candidate_text'],
                        'human_label': labels[c['candidate_id']],
                    }
                    for c in candidates
                ],
            }
            buckets[bucket].append(curated)
    selected: list[dict[str, Any]] = []
    for bucket, count in TARGET_COUNTS.items():
        selected.extend(buckets[bucket][:count])
    selected = selected[:total_examples]
    if len(selected) < total_examples:
        leftovers: list[dict[str, Any]] = []
        for bucket in TARGET_COUNTS:
            leftovers.extend(buckets[bucket][TARGET_COUNTS[bucket]:])
        selected.extend(leftovers[: total_examples - len(selected)])
    return selected


def write_dataset(examples: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(examples, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description='Build curated DSPy judge examples from prior eval artifacts')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--smoke-out', type=Path, default=DEFAULT_SMOKE_OUT)
    parser.add_argument('--total-examples', type=int, default=100)
    args = parser.parse_args()

    examples = curate_examples(DEFAULT_SOURCES, args.total_examples)
    write_dataset(examples, args.out)
    write_dataset(examples[:12], args.smoke_out)
    counts: dict[str, int] = {}
    for ex in examples:
        judge = json.loads(ex['judge_json'])
        winner = judge['selected_candidate_id']
        label = next(c['human_label']['label'] for c in ex['candidate_labels'] if c['candidate_id'] == winner)
        counts[label] = counts.get(label, 0) + 1
    print(f'[SAVE] wrote {len(examples)} examples -> {args.out}')
    print(f'[SAVE] wrote {min(12, len(examples))} smoke examples -> {args.smoke_out}')
    print('[BUCKETS]', json.dumps(counts, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
