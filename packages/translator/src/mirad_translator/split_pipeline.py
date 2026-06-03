from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import dspy
from pydantic import BaseModel, Field

from mirad_translator.translate import DefaultTranslator


def strip_punct(text: str) -> str:
    text = re.sub(r'[.,!?;:()"\'\[\]{}]', '', str(text or ''))
    return re.sub(r'\s+', ' ', text).strip().lower()


def tokenize(text: str) -> list[str]:
    return [t for t in strip_punct(text).split(' ') if t]


def sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, strip_punct(a), strip_punct(b)).ratio()


def jaccard_similarity(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    hay = strip_punct(text)
    return any(n in hay for n in needles)


def infer_taxonomy_focus(source_text: str, expected_text: str, candidate_text: str) -> list[str]:
    tags: list[str] = []
    src = str(source_text or '').lower()
    gold = str(expected_text or '').lower()
    pred = str(candidate_text or '').lower()
    if ' not ' in f' {src} ' or ' voy ' in f' {gold} ' or ' von ' in f' {gold} ':
        tags.append('negation')
    if 'would' in src or 'hypothetical' in src:
        tags.append('hypothetical')
    if 'will' in src or 'future' in src:
        tags.append('future')
    if 'was ' in src or 'were ' in src or 'has ' in src or 'have ' in src:
        tags.append('tense_aspect')
    if ' he ' in f' {src} ' or ' she ' in f' {src} ' or ' they ' in f' {src} ' or ' you all' in src or ' we ' in f' {src} ':
        tags.append('pronouns')
    if ' is ' in f' {src} ' or ' are ' in f' {src} ' or ' am ' in f' {src} ':
        tags.append('copula')
    if pred.endswith('?') or '?' in src:
        tags.append('question')
    if len(tags) == 0:
        tags.append('lexical_choice')
    return sorted(set(tags))


def _heuristic_penalty(source_text: str, expected_text: str, candidate_text: str) -> float:
    penalty = 0.0
    pred = strip_punct(candidate_text)
    gold = strip_punct(expected_text)
    if ' eyt ' in f' {pred} ' and ' yet ' in f' {gold} ':
        penalty += 0.12
    if pred.count(' it ') > gold.count(' it ') + 1:
        penalty += 0.18
    if pred.count(' ey ') > 0 and pred.count(' it ') > gold.count(' it '):
        penalty += 0.12
    if ' voy ' in f' {gold} ' and ' voy ' not in f' {pred} ' and ' not ' in f' {source_text.lower()} ':
        penalty += 0.25
    if ' se ' in f' {gold} ' and ' se ' not in f' {pred} ' and any(x in source_text.lower() for x in [' is ', ' are ', ' am ', ' was ', ' were ']):
        penalty += 0.08
    if len(tokenize(candidate_text)) > len(tokenize(expected_text)) + 4:
        penalty += 0.08
    return penalty


@dataclass
class CandidateAssessment:
    aggregate_score: float
    label: str
    notes: str
    criteria_scores: dict[str, float]
    error_tags: list[str]


class JudgeDecisionModel(BaseModel):
    selected_candidate_id: str
    candidate_scores: dict[str, float] = Field(default_factory=dict)
    ranking: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    rationale: str = ''


class CuratedJudgeExampleModel(BaseModel):
    example_id: str
    source_text: str
    expected_text: str
    candidate_payload_json: str
    judge_json: str
    rationale: str = ''
    source_reference: str = ''
    taxonomy_focus: list[str] = Field(default_factory=list)


def assess_candidate(*, source_text: str, expected_text: str, candidate_text: str) -> CandidateAssessment:
    exact = candidate_text.strip() == expected_text.strip()
    stripped_exact = strip_punct(candidate_text) == strip_punct(expected_text)
    seq = sequence_similarity(candidate_text, expected_text)
    jac = jaccard_similarity(candidate_text, expected_text)
    sim = max(seq, jac)
    penalty = _heuristic_penalty(source_text, expected_text, candidate_text)

    if exact:
        base = 0.99
        label = 'exact_match'
        notes = 'Candidate preserves the full source meaning with strong Mirad grammar and morphology.'
    elif stripped_exact:
        base = 0.95
        label = 'punctuation_variant'
        notes = 'Only punctuation or casing differs from the reference.'
    elif sim >= 0.88 and penalty <= 0.06:
        base = 0.88
        label = 'likely_valid_alternative'
        notes = 'Likely valid alternative or very close lexical variant.'
    elif sim >= 0.72:
        base = 0.64
        label = 'minor_error'
        notes = 'Mostly right, but contains a minor lexical or morphology issue.'
    elif sim >= 0.5:
        base = 0.38
        label = 'major_error'
        notes = 'Partially related, but meaning or grammar is materially wrong.'
    else:
        base = 0.12
        label = 'completely_wrong'
        notes = 'Completely wrong or badly malformed translation.'

    aggregate = max(0.0, min(1.0, round(base - penalty, 2)))

    if aggregate >= 0.93:
        sem = 0.98
        grammar = 0.96
        morph = 0.96
        fluency = 0.95
    elif aggregate >= 0.82:
        sem = 0.9
        grammar = 0.86
        morph = 0.84
        fluency = 0.86
    elif aggregate >= 0.58:
        sem = 0.72
        grammar = 0.62
        morph = 0.58
        fluency = 0.68
    elif aggregate >= 0.3:
        sem = 0.45
        grammar = 0.38
        morph = 0.34
        fluency = 0.42
    else:
        sem = 0.18
        grammar = 0.16
        morph = 0.12
        fluency = 0.18

    error_tags = infer_taxonomy_focus(source_text, expected_text, candidate_text)
    if label in {'minor_error', 'major_error', 'completely_wrong'}:
        error_tags.append(label)

    return CandidateAssessment(
        aggregate_score=aggregate,
        label=label,
        notes=notes,
        criteria_scores={
            'semantic_fidelity': round(sem, 2),
            'grammar': round(grammar, 2),
            'morphology': round(morph, 2),
            'fluency': round(fluency, 2),
        },
        error_tags=sorted(set(error_tags)),
    )


def build_gold_judge_json(example: dict[str, Any]) -> str:
    if 'judge_json' in example:
        return str(example['judge_json'])
    candidates = example['candidates']
    ranked = sorted(candidates, key=lambda item: (-float(item['human_label']['aggregate_score']), int(item['human_label']['rank']), item['candidate_id']))
    winner = ranked[0]
    payload = JudgeDecisionModel(
        selected_candidate_id=winner['candidate_id'],
        candidate_scores={c['candidate_id']: round(float(c['human_label']['aggregate_score']), 2) for c in candidates},
        ranking=[c['candidate_id'] for c in ranked],
        confidence=round(min(0.99, max(0.55, float(winner['human_label']['aggregate_score']) + 0.08)), 2),
        rationale=example.get('rationale') or winner['human_label'].get('notes') or 'Select the highest-quality translation candidate.',
    )
    return payload.model_dump_json(exclude_none=True)


class SplitJudgeSignature(dspy.Signature):
    """Select and score the best translation candidate."""

    source_text: str = dspy.InputField(desc='Original source sentence')
    candidate_payload_json: str = dspy.InputField(desc='JSON array of candidate_id and candidate_text records')
    judge_json: str = dspy.OutputField(desc='JSON object: selected_candidate_id, candidate_scores, ranking, confidence, rationale')


class SplitJudgeModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(SplitJudgeSignature)

    def forward(self, *, source_text: str, candidate_payload_json: str) -> dspy.Prediction:
        return self.predict(
            source_text=source_text,
            candidate_payload_json=candidate_payload_json,
        )


def parse_judge_json(raw: str, candidate_ids: Iterable[str]) -> dict[str, Any]:
    text = str(raw or '').strip()
    if '```' in text:
        text = re.sub(r'^```(?:json)?|```$', '', text, flags=re.MULTILINE).strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end >= start:
        text = text[start:end + 1]
    payload = json.loads(text)
    model = JudgeDecisionModel.model_validate(payload)
    valid_ids = list(candidate_ids)
    selected = model.selected_candidate_id.strip()
    if selected not in valid_ids:
        raise ValueError(f'selected_candidate_id not in candidates: {selected}')
    candidate_scores = model.candidate_scores
    normalized_scores: dict[str, float] = {}
    for cid in valid_ids:
        raw_score = candidate_scores.get(cid, 0.0)
        try:
            score = float(raw_score)
        except Exception:
            score = 0.0
        normalized_scores[cid] = max(0.0, min(1.0, score))
    ranking = model.ranking
    ranking = [str(x) for x in ranking if str(x) in valid_ids]
    for cid in valid_ids:
        if cid not in ranking:
            ranking.append(cid)
    confidence = model.confidence or normalized_scores.get(selected, 0.5)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = normalized_scores.get(selected, 0.5)
    confidence = max(0.0, min(1.0, confidence))
    rationale = model.rationale.strip()
    return {
        'selected_candidate_id': selected,
        'candidate_scores': normalized_scores,
        'ranking': ranking,
        'confidence': confidence,
        'rationale': rationale,
    }


def judge_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    candidate_payload = json.loads(example.candidate_payload_json)
    candidate_ids = [row['candidate_id'] if isinstance(row, dict) else str(row) for row in candidate_payload]
    gold = parse_judge_json(example.judge_json, candidate_ids)
    try:
        pred = parse_judge_json(getattr(prediction, 'judge_json', ''), candidate_ids)
    except Exception:
        return 0.0
    winner_score = 1.0 if pred['selected_candidate_id'] == gold['selected_candidate_id'] else 0.0
    rank_overlap = 0.0
    if pred['ranking'] and gold['ranking']:
        rank_overlap = len(set(pred['ranking'][:2]) & set(gold['ranking'][:2])) / max(1, len(set(gold['ranking'][:2])))
    mae = 0.0
    ids = list(gold['candidate_scores'].keys())
    if ids:
        mae = sum(abs(pred['candidate_scores'].get(cid, 0.0) - gold['candidate_scores'][cid]) for cid in ids) / len(ids)
    score_fit = max(0.0, 1.0 - mae)
    return round((0.65 * winner_score) + (0.15 * rank_overlap) + (0.20 * score_fit), 4)


def _candidate_text(candidate: dict[str, Any]) -> str:
    return str(candidate.get('candidate_text') or candidate.get('mirad') or candidate.get('prediction') or '')


def example_to_dspy(example: dict[str, Any]) -> dspy.Example:
    if 'candidate_payload_json' in example and 'judge_json' in example:
        fields = CuratedJudgeExampleModel(
            example_id=str(example.get('example_id') or example.get('id') or ''),
            source_text=str(example['source_text']),
            expected_text=str(example.get('expected_text') or ''),
            candidate_payload_json=str(example['candidate_payload_json']),
            judge_json=build_gold_judge_json(example),
            rationale=str(example.get('rationale') or ''),
            source_reference=str(example.get('source_reference') or ''),
            taxonomy_focus=list(example.get('taxonomy_focus') or []),
        )
        return dspy.Example(**fields.model_dump()).with_inputs('source_text', 'candidate_payload_json')

    candidate_payload = [
        {
            'candidate_id': c['candidate_id'],
            'candidate_text': _candidate_text(c),
        }
        for c in example['candidates']
    ]
    return dspy.Example(
        example_id=example['id'],
        source_text=example['source_text'],
        expected_text=example['expected_text'],
        candidate_payload_json=json.dumps(candidate_payload, ensure_ascii=False),
        judge_json=build_gold_judge_json(example),
        rationale=example.get('rationale', ''),
        source_reference=example.get('source_reference', ''),
        taxonomy_focus=example.get('taxonomy_focus', []),
    ).with_inputs('source_text', 'candidate_payload_json')


def load_curated_judge_dataset(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(payload, list):
        raise ValueError('curated judge dataset must be a list')
    return payload


def make_deepinfra_lm(*, model: str | None = None, temperature: float = 0.0, max_tokens: int = 2048) -> dspy.LM:
    api_key = os.environ.get('DEEPINFRA_API_KEY', '')
    if not api_key:
        raise ValueError('DEEPINFRA_API_KEY not set')
    api_base = os.environ.get('DEEPINFRA_BASE_URL', 'https://api.deepinfra.com/v1/openai')
    model_name = model or os.environ.get('DEEPINFRA_TRANSLATION_MODEL', 'deepseek-ai/DeepSeek-V4-Flash')
    return dspy.LM(
        model=f'openai/{model_name}',
        temperature=temperature,
        cache=False,
        api_key=api_key,
        api_base=api_base,
        max_tokens=max_tokens,
        num_retries=3,
    )


def load_generator_pairs(json_path: str | Path, max_samples: int | None = None, seed: int = 42) -> list[dspy.Example]:
    import random

    raw = json.loads(Path(json_path).read_text(encoding='utf-8'))
    pairs = raw.get('pairs', raw) if isinstance(raw, dict) else raw
    examples = []
    for item in pairs:
        english = item.get('english_text') or item.get('english') or item.get('source') or ''
        mirad = item.get('mirad_text') or item.get('mirad') or item.get('target') or ''
        if english and mirad:
            examples.append(dspy.Example(english_text=english, mirad_text=mirad).with_inputs('english_text'))
    if max_samples and len(examples) > max_samples:
        rng = random.Random(seed)
        rng.shuffle(examples)
        examples = examples[:max_samples]
    return examples


def normalized_match_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    return 1.0 if strip_punct(example.mirad_text) == strip_punct(getattr(prediction, 'mirad_text', '')) else 0.0


def exact_match_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    return 1.0 if str(example.mirad_text).strip() == str(getattr(prediction, 'mirad_text', '')).strip() else 0.0


def build_generator_module(*, num_context_passages: int = 3, top_k_per_word: int = 2) -> dspy.Module:
    return DefaultTranslator(
        num_context_passages=num_context_passages,
        top_k_per_word=top_k_per_word,
        use_compiled=False,
        semantic_lexicon=False,
    )


def generate_candidates_with_module(generator: dspy.Module, english_text: str, temperatures: list[float], candidate_count: int) -> list[dict[str, Any]]:
    candidates = []
    for index in range(candidate_count):
        temp = temperatures[index % len(temperatures)]
        with dspy.context(lm=make_deepinfra_lm(temperature=temp, max_tokens=4096)):
            pred = generator(english_text=english_text)
        candidates.append(
            {
                'candidate_id': f'cand-{index + 1}',
                'candidate_text': str(getattr(pred, 'mirad_text', '')),
                'temperature': temp,
                'raw_prediction': {
                    'mirad_text': str(getattr(pred, 'mirad_text', '')),
                    'context': getattr(pred, 'context', []),
                    'used_rule_ids': getattr(pred, 'used_rule_ids', []),
                },
            }
        )
    return candidates


def pick_best_with_judge(judge: dspy.Module, english_text: str, gold_text: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_payload = [
        {
            'candidate_id': c['candidate_id'],
            'candidate_text': c['candidate_text'],
        }
        for c in candidates
    ]
    pred = judge(
        source_text=english_text,
        candidate_payload_json=json.dumps(candidate_payload, ensure_ascii=False),
    )
    parsed = parse_judge_json(getattr(pred, 'judge_json', ''), [c['candidate_id'] for c in candidates])
    by_id = {c['candidate_id']: c for c in candidates}
    best = by_id[parsed['selected_candidate_id']]
    ranked = []
    for rank, cid in enumerate(parsed['ranking']):
        row = dict(by_id[cid])
        row['rank'] = rank
        row['winner'] = cid == parsed['selected_candidate_id']
        row['human_score'] = parsed['candidate_scores'].get(cid, 0.0)
        ranked.append(row)
    return {
        'best_candidate': best,
        'judge': parsed,
        'ranked_candidates': ranked,
    }
