"""
TranslatorAdapter — standardized interface between the eval script and the
actual translation implementation.

The eval script is agnostic to whether translation uses DefaultTranslator,
compiled programs, Ollama, or a custom DSPy module. All it sees is this
Adapter interface.

Adapter interface:
  adapter = TranslatorAdapter(config: dict)
  result  = adapter.translate(source_text: str)  → TranslationResult

TranslationResult:
  .translated_text   str     — the model's translation output
  .word_equivalents  dict    — {english_word: mirad_word} or {mirad_word: english_word}
  .context_passages  list[str] — retrieved grammar rule passages used
  .used_rule_ids     list[str] — IDs of retrieved rules consumed by the model
  .raw_prediction    object  — raw DSPy Prediction (for debugging)
  .timing_ms         dict    — {"total": ms, "model_call": ms, ...}

All timing is measured in milliseconds.
"""
from __future__ import annotations

import os, time, importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class TranslationResult:
    """Standardized translation result returned by all adapter implementations."""
    translated_text: str
    word_equivalents: dict[str, str] = field(default_factory=dict)
    context_passages: list[str] = field(default_factory=list)
    used_rule_ids: list[str] = field(default_factory=list)
    # Timing breakdown (ms)
    total_ms: float = 0.0
    model_call_ms: float = 0.0
    lookup_ms: float = 0.0
    retrieval_ms: float = 0.0
    # Raw DSPy Prediction for introspection
    raw: Any = None

    def to_dict(self) -> dict:
        return {
            "translated_text": self.translated_text,
            "word_equivalents": self.word_equivalents,
            "context_passages": self.context_passages,
            "used_rule_ids": self.used_rule_ids,
            "total_ms": round(self.total_ms, 1),
            "model_call_ms": round(self.model_call_ms, 1),
            "lookup_ms": round(self.lookup_ms, 1),
            "retrieval_ms": round(self.retrieval_ms, 1),
        }


# ── Base adapter ─────────────────────────────────────────────────────────────

class TranslatorAdapter:
    """Base class for translator adapters. Subclass to add new implementations."""

    def __init__(self, config: dict):
        self.config = config
        self._direction = config.get("data", {}).get("direction", "en_to_mir")
        self._translator_cfg = config.get("translator", {})

    def translate(self, source_text: str) -> TranslationResult:
        raise NotImplementedError

    @property
    def direction(self) -> str:
        return self._direction

    def close(self):
        """Clean up any resources (sessions, connections). Override if needed."""
        pass


# ── DefaultTranslator adapter ─────────────────────────────────────────────────

class DefaultTranslatorAdapter(TranslatorAdapter):
    """Adapter for the project's DefaultTranslator factory.

    Wraps the DSPy-based En→Mir / Mir→En translator with standardized timing
    and result extraction. Keeps the eval script completely agnostic to the
    internal structure of TranslatorModule / MiradToEnglishModule.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self._setup_dspy()
        self._translator = self._build_translator()

    def _setup_dspy(self):
        """Configure the DSPy LM once per adapter instance."""
        model_cfg  = self.config.get("model", {})
        api_key    = os.environ.get(model_cfg.get("api_key_env", "DEEPINFRA_API_KEY"))
        api_base   = model_cfg.get("api_base", "https://api.deepinfra.com/v1/openai")
        model_name = model_cfg.get("model", "deepseek-ai/DeepSeek-V4-Flash")
        timeout    = model_cfg.get("timeout", 120)

        lm = dspy.LM(
            model=f"openai/{model_name}",
            api_key=api_key,
            api_base=api_base,
            timeout=timeout,
        )
        dspy.settings.configure(lm=lm)

    def _build_translator(self):
        """Build the translator from config. Returns a callable dspy.Module."""
        from mirad_translator.translate import DefaultTranslator

        tcfg = self._translator_cfg
        self._db_path = tcfg.get("db_path", str(_PROJECT_ROOT / "data" / "mirad-db.sqlite"))
        self._direction = self._direction

        return DefaultTranslator(
            db_path=self._db_path,
            num_context_passages=tcfg.get("num_context_passages", 5),
            max_retries=0,          # eval script handles its own retries if needed
            num_hops=1,
            direction=self._direction,
            use_postprocessor=tcfg.get("use_postprocessor", True),
            use_compiled=tcfg.get("use_compiled", False),
            semantic_lexicon=tcfg.get("semantic_lexicon", True),
            top_k_per_word=tcfg.get("top_k_per_word", 0),
            max_total_pairs=tcfg.get("max_total_pairs", 50),
            min_similarity=tcfg.get("min_similarity", 0.5),
        )

    def translate(self, source_text: str) -> TranslationResult:
        """Call the translator and extract a standardized TranslationResult."""
        t0 = time.perf_counter()
        t_lookup = 0.0
        t_retrieval = 0.0

        # Extract timing from the translator's internal retrieval if available.
        # MiradContextRetrieve and MiradLexiconLookup are called inside the module.
        pred = self._translator(**self._input_field(source_text))

        t_total = (time.perf_counter() - t0) * 1000

        return TranslationResult(
            translated_text=self._extract_text(pred),
            word_equivalents=self._extract_word_equivalents(pred),
            context_passages=self._extract_context(pred),
            used_rule_ids=self._extract_rule_ids(pred),
            total_ms=t_total,
            model_call_ms=t_total,     # model_call is the dominant cost
            lookup_ms=t_lookup,
            retrieval_ms=t_retrieval,
            raw=pred,
        )

    def _input_field(self, text: str) -> dict:
        """Build the kwargs dict for the translator's forward() method."""
        if self._direction == "en_to_mir":
            return {"english_text": text}
        return {"mirad_text": text}

    def _extract_text(self, pred) -> str:
        if self._direction == "en_to_mir":
            return str(pred.mirad_text).strip()
        return str(pred.english_text).strip()

    def _extract_word_equivalents(self, pred) -> dict:
        we = getattr(pred, "word_equivalents", None)
        if we is None:
            return {}
        if isinstance(we, dict):
            return we
        return {}

    def _extract_context(self, pred) -> list[str]:
        ctx = getattr(pred, "context", None)
        if ctx is None:
            return []
        if isinstance(ctx, list):
            return [str(p) for p in ctx]
        return [str(ctx)]

    def _extract_rule_ids(self, pred) -> list[str]:
        ids = getattr(pred, "used_rule_ids", None)
        if ids is None:
            return []
        if isinstance(ids, list):
            return [str(i) for i in ids]
        return [str(ids)]


# ── Adapter registry ──────────────────────────────────────────────────────────

_ADAPTERS: dict[str, type[TranslatorAdapter]] = {
    "default": DefaultTranslatorAdapter,
    # "compiled": CompiledTranslatorAdapter,   # future
    # "ollama":   OllamaTranslatorAdapter,      # future
}


def build_adapter(config: dict) -> TranslatorAdapter:
    """Factory: build the right adapter from the config dict."""
    tcfg = config.get("translator", {})
    adapter_type = tcfg.get("type", "default")

    if adapter_type in _ADAPTERS:
        adapter_cls = _ADAPTERS[adapter_type]
    else:
        # Try loading as a Python import path: "mypackage.MyAdapter"
        try:
            module_path, class_name = adapter_type.rsplit(".", 1)
            mod = importlib.import_module(module_path)
            adapter_cls = getattr(mod, class_name)
        except Exception as exc:
            raise ValueError(
                f"Unknown translator type '{adapter_type}'. "
                f"Available: {list(_ADAPTERS)} or a Python import path. "
                f"Error: {exc}"
            )

    return adapter_cls(config)