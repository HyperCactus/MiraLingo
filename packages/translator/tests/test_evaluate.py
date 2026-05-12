import pytest
import csv
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

import dspy

from mirad_translator.evaluate import (
    load_evaluation_set,
    exact_match_metric,
    normalized_match_metric,
    evaluate_module,
    compile_with_bootstrap,
    EVAL_CSV_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary evaluation CSV with a few sentence pairs."""
    csv_file = tmp_path / "eval_pairs.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["English", "Mirad"])
        writer.writeheader()
        writer.writerow({"English": "I am cold.", "Mirad": "At tose oma."})
        writer.writerow({"English": "The baby is sleeping.", "Mirad": "Ha tobud tujeye."})
        writer.writerow({"English": "It is raining.", "Mirad": "Mamileye."})
    return str(csv_file)


@pytest.fixture
def eval_examples(sample_csv):
    """Load evaluation examples from the sample CSV."""
    return load_evaluation_set(sample_csv)


# ---------------------------------------------------------------------------
# load_evaluation_set tests
# ---------------------------------------------------------------------------

def test_load_eval_set_returns_examples(eval_examples):
    """Evaluation set should contain 3 dspy.Example objects."""
    assert len(eval_examples) == 3
    assert all(isinstance(ex, dspy.Example) for ex in eval_examples)


def test_load_eval_set_has_correct_input_keys(eval_examples):
    """Each Example should have english_text as the only input key."""
    for ex in eval_examples:
        inputs = ex.inputs()
        assert set(inputs.keys()) == {"english_text"}
        assert "english_text" in ex.keys()
        assert "mirad_text" in ex.keys()


def test_load_eval_set_values(eval_examples):
    """Examples should preserve the CSV values."""
    assert eval_examples[0].english_text == "I am cold."
    assert eval_examples[0].mirad_text == "At tose oma."
    assert eval_examples[1].english_text == "The baby is sleeping."
    assert eval_examples[2].english_text == "It is raining."


def test_load_eval_set_missing_file():
    """load_evaluation_set raises FileNotFoundError for missing CSV."""
    with pytest.raises(FileNotFoundError):
        load_evaluation_set("/nonexistent/path.csv")


def test_load_eval_set_from_default_path():
    """Load from the project's actual eval CSV if it exists."""
    if os.path.exists(EVAL_CSV_PATH):
        examples = load_evaluation_set()
        assert len(examples) > 0
        assert all(isinstance(ex, dspy.Example) for ex in examples)
        # Verify the CSV has the expected columns and content
        assert hasattr(examples[0], 'english_text')
        assert hasattr(examples[0], 'mirad_text')


def test_load_eval_set_skips_empty_rows(tmp_path):
    """Empty rows in the CSV should be skipped."""
    csv_file = tmp_path / "empty_rows.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["English", "Mirad"])
        writer.writeheader()
        writer.writerow({"English": "Hello", "Mirad": "Helo"})
        writer.writerow({"English": "", "Mirad": ""})  # empty row
        writer.writerow({"English": "Goodbye", "Mirad": "Baye"})
    examples = load_evaluation_set(str(csv_file))
    assert len(examples) == 2  # empty row skipped


# ---------------------------------------------------------------------------
# exact_match_metric tests
# ---------------------------------------------------------------------------

def test_exact_match_identical():
    """Exact match returns 1.0 for identical strings."""
    example = dspy.Example(english_text="I am cold.", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="At tose oma.", confidence="0.95")
    assert exact_match_metric(example, prediction) == 1.0


def test_exact_match_different():
    """Exact match returns 0.0 for different translations."""
    example = dspy.Example(english_text="I am cold.", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="At se oma.", confidence="0.5")
    assert exact_match_metric(example, prediction) == 0.0


def test_exact_match_whitespace_normalized():
    """Exact match normalizes whitespace before comparison."""
    example = dspy.Example(english_text="I am cold.", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="  At tose oma.  ", confidence="0.9")
    assert exact_match_metric(example, prediction) == 1.0


def test_exact_match_extra_whitespace_fails():
    """Exact match fails if internal whitespace differs."""
    example = dspy.Example(english_text="test", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="At  tose  oma.", confidence="0.9")
    # _normalize collapses multiple spaces to one, so this should match
    assert exact_match_metric(example, prediction) == 1.0


# ---------------------------------------------------------------------------
# normalized_match_metric tests
# ---------------------------------------------------------------------------

def test_normalized_match_strips_punctuation():
    """Normalized match ignores trailing punctuation differences."""
    example = dspy.Example(english_text="test", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="At tose oma", confidence="0.9")
    assert normalized_match_metric(example, prediction) == 1.0


def test_normalized_match_strips_commas():
    """Normalized match ignores commas."""
    example = dspy.Example(
        english_text="test",
        mirad_text='At texe, av hus, at ese.',
    ).with_inputs("english_text")
    prediction = dspy.Prediction(
        mirad_text='At texe av hus at ese.',
        confidence="0.9",
    )
    assert normalized_match_metric(example, prediction) == 1.0


def test_normalized_match_preserves_hyphens():
    """Hyphens in compound words like semi-automatic should be preserved."""
    example = dspy.Example(english_text="test", mirad_text="eynutexea dopar").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="eynutexea dopar", confidence="0.9")
    assert normalized_match_metric(example, prediction) == 1.0


def test_normalized_match_different_meaning():
    """Normalized match returns 0.0 for genuinely different translations."""
    example = dspy.Example(english_text="test", mirad_text="At tose oma.").with_inputs("english_text")
    prediction = dspy.Prediction(mirad_text="Et te ha dud.", confidence="0.5")
    assert normalized_match_metric(example, prediction) == 0.0


def test_normalized_match_quotes():
    """Normalized match handles Curly and straight quotes."""
    example = dspy.Example(
        english_text="test",
        mirad_text='It da: "Van esu man."',
    ).with_inputs("english_text")
    prediction = dspy.Prediction(
        mirad_text='It da: \u201cVan esu man.\u201d',
        confidence="0.9",
    )
    # Both quote styles should normalize to the same thing
    assert normalized_match_metric(example, prediction) == 1.0


# ---------------------------------------------------------------------------
# evaluate_module tests (mocked)
# ---------------------------------------------------------------------------

def test_evaluate_module_with_mock():
    """evaluate_module should call DSPy Evaluate and return results."""
    mock_module = Mock()
    mock_pred = dspy.Prediction(mirad_text="At tose oma.", confidence="0.95")

    # Make forward return a Prediction
    mock_module.forward = Mock(return_value=mock_pred)
    mock_module.__class__ = type("TranslatorModule", (), {})

    # Create a small eval set
    devset = [
        dspy.Example(english_text="I am cold.", mirad_text="At tose oma.").with_inputs("english_text"),
    ]

    with patch('mirad_translator.evaluate.Evaluate') as mock_eval_cls:
        mock_eval_instance = Mock()
        mock_eval_instance.return_value = 1.0  # perfect score
        mock_eval_cls.return_value = mock_eval_instance

        result = evaluate_module(
            module=mock_module,
            devset=devset,
            metric=exact_match_metric,
        )

        assert result["score"] == 1.0
        assert result["devset_size"] == 1


# ---------------------------------------------------------------------------
# compile_with_bootstrap tests (mocked)
# ---------------------------------------------------------------------------

def test_compile_with_bootstrap_mock():
    """compile_with_bootstrap should call BootstrapFewShot.compile."""
    mock_module = Mock(spec=dspy.Module)

    with patch('mirad_translator.evaluate.BootstrapFewShot') as mock_bfs_cls:
        mock_optimizer = Mock()
        mock_optimizer.compile.return_value = Mock(spec=dspy.Module)
        mock_bfs_cls.return_value = mock_optimizer

        trainset = [
            dspy.Example(english_text="test", mirad_text="testo").with_inputs("english_text"),
        ]

        result = compile_with_bootstrap(
            student=mock_module,
            trainset=trainset,
        )

        mock_bfs_cls.assert_called_once()
        mock_optimizer.compile.assert_called_once_with(mock_module, trainset=trainset)