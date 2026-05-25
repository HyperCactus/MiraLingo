import json
from copy import deepcopy
from pathlib import Path

import pytest

DEVSET_PATH = Path("data/eval/devset_s01_bidirectional.json")
REQUIRED_FIELDS = {
    "id",
    "direction",
    "source_text",
    "expected_text",
    "rationale",
    "taxonomy_focus",
    "source_reference",
}
ALLOWED_DIRECTIONS = {"en_to_mir", "mir_to_en"}
SECRET_LIKE_FIELDS = {
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "authorization",
    "auth",
    "private_key",
}


def load_devset(path: Path = DEVSET_PATH):
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_devset(payload)
    return payload


def validate_devset(payload):
    assert isinstance(payload, list), "dev-set must be a list"
    assert 10 <= len(payload) <= 15, f"dev-set size must be between 10 and 15, got {len(payload)}"

    ids = set()
    directions = set()

    for index, example in enumerate(payload, start=1):
        example_id = example.get("id", f"index-{index}")
        assert isinstance(example, dict), f"{example_id}: each example must be an object"

        missing = sorted(REQUIRED_FIELDS - set(example))
        assert not missing, f"{example_id}: missing required fields {missing}"

        assert example_id not in ids, f"{example_id}: duplicate id"
        ids.add(example_id)

        direction = example["direction"]
        assert direction in ALLOWED_DIRECTIONS, f"{example_id}: unknown direction '{direction}'"
        directions.add(direction)

        for field in ("id", "direction", "source_text", "expected_text", "rationale"):
            value = example[field]
            assert isinstance(value, str) and value.strip(), f"{example_id}: field '{field}' must be a non-empty string"

        taxonomy_focus = example["taxonomy_focus"]
        assert isinstance(taxonomy_focus, list) and taxonomy_focus, f"{example_id}: taxonomy_focus must be a non-empty list"
        assert all(isinstance(item, str) and item.strip() for item in taxonomy_focus), (
            f"{example_id}: taxonomy_focus entries must be non-empty strings"
        )

        source_reference = example["source_reference"]
        assert isinstance(source_reference, dict), f"{example_id}: source_reference must be an object"
        assert source_reference.get("type") in {"csv", "note"}, (
            f"{example_id}: source_reference.type must be 'csv' or 'note'"
        )
        if source_reference["type"] == "csv":
            assert source_reference.get("path") == "data/phrases/english-mirad-sentence-pairs.csv", (
                f"{example_id}: csv source_reference.path must point at the phrase CSV"
            )
            line = source_reference.get("line")
            assert isinstance(line, int) and line >= 2, f"{example_id}: csv source_reference.line must be an integer >= 2"
        else:
            note = source_reference.get("note")
            assert isinstance(note, str) and note.strip(), f"{example_id}: note source_reference.note must be non-empty"

        lowered_keys = {key.lower() for key in example}
        found_secret_keys = sorted(lowered_keys & SECRET_LIKE_FIELDS)
        assert not found_secret_keys, f"{example_id}: secret-like fields are forbidden: {found_secret_keys}"

    assert directions == ALLOWED_DIRECTIONS, f"dev-set must include both directions, got {sorted(directions)}"


def test_devset_fixture_passes_structural_contract():
    devset = load_devset()
    assert len(devset) == 12


def test_devset_ids_are_unique_and_stable():
    devset = load_devset()
    ids = [example["id"] for example in devset]
    assert ids == sorted(ids)
    assert all(example_id.startswith("s01-") for example_id in ids)


def test_devset_uses_only_non_secret_schema_fields():
    devset = load_devset()
    for example in devset:
        assert set(example) == REQUIRED_FIELDS


def test_validate_devset_rejects_missing_direction():
    devset = load_devset()
    broken = deepcopy(devset)
    del broken[0]["direction"]
    with pytest.raises(AssertionError, match="missing required fields"):
        validate_devset(broken)


def test_validate_devset_rejects_empty_rationale():
    devset = load_devset()
    broken = deepcopy(devset)
    broken[0]["rationale"] = "   "
    with pytest.raises(AssertionError, match="rationale"):
        validate_devset(broken)


def test_validate_devset_rejects_duplicate_id():
    devset = load_devset()
    broken = deepcopy(devset)
    broken[1]["id"] = broken[0]["id"]
    with pytest.raises(AssertionError, match="duplicate id"):
        validate_devset(broken)


def test_validate_devset_rejects_too_few_examples():
    devset = load_devset()
    broken = deepcopy(devset[:9])
    with pytest.raises(AssertionError, match="between 10 and 15"):
        validate_devset(broken)


def test_validate_devset_rejects_too_many_examples():
    devset = load_devset()
    broken = deepcopy(devset)
    extra = deepcopy(broken[0])
    extra["id"] = "s01-013-extra-copy"
    broken.extend([deepcopy(extra) for _ in range(4)])
    for index, item in enumerate(broken[12:], start=13):
        item["id"] = f"s01-{index:03d}-extra-copy"
    with pytest.raises(AssertionError, match="between 10 and 15"):
        validate_devset(broken)


def test_validate_devset_rejects_unknown_direction_with_offending_id():
    devset = load_devset()
    broken = deepcopy(devset)
    broken[0]["direction"] = "english_to_mirad"
    with pytest.raises(AssertionError, match=f"{broken[0]['id']}: unknown direction"):
        validate_devset(broken)
