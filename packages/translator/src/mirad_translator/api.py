from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Literal
import logging
import os
import traceback
from pathlib import Path

import dspy
from dotenv import load_dotenv

from mirad_translator.translate import DefaultTranslator

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TRANSLATION_MODEL = "deepseek-ai/DeepSeek-V4-Flash"

app = FastAPI()

# Global translator instances — initialized lazily
translator_en_mir = None
translator_mir_en = None


def _configure_default_lm() -> str:
    """Configure DSPy with the default DeepInfra translation model."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPINFRA_API_KEY is not set")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    model = os.environ.get("DEEPINFRA_TRANSLATION_MODEL") or os.environ.get(
        "DEEPINFRA_TEACHER_MODEL",
        DEFAULT_TRANSLATION_MODEL,
    )
    dspy.settings.configure(
        lm=dspy.LM(
            model=f"openai/{model}",
            api_key=api_key,
            api_base=api_base,
        )
    )
    return model


@app.on_event("startup")
async def startup_event():
    global translator_en_mir, translator_mir_en
    try:
        model = _configure_default_lm()
        translator_en_mir = DefaultTranslator(direction="en_to_mir")
        translator_mir_en = DefaultTranslator(direction="mir_to_en")
        logger.info("Translators initialized successfully with DeepInfra model %s", model)
    except Exception as e:
        logger.warning(
            "Translator initialization deferred: %s. "
            "Health endpoint will report unhealthy until DeepInfra env vars are configured.",
            e,
        )


@app.get("/")
async def root():
    return {"message": "Mirad Translator API", "directions": ["en_to_mir", "mir_to_en"]}


@app.get("/health")
async def health():
    if translator_en_mir is None or translator_mir_en is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "Translators not initialized"}
        )
    try:
        # Test both directions enough to catch missing LM/env without exhausting API budget.
        result = translator_en_mir(english_text="you do not work at home")
        if not result.mirad_text:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "unhealthy", "reason": "En→Mir translator returned empty result"}
            )
    except Exception as e:
        logging.error("Health check failed: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "Translator health check failed"}
        )

    return {"status": "healthy"}


class TranslateRequest(BaseModel):
    text: str
    direction: Literal["en_to_mir", "mir_to_en"] = "en_to_mir"
    retrieve: bool = False


class TranslateResponse(BaseModel):
    text: str
    translation: str
    direction: str
    confidence: Optional[str] = None
    word_equivalents: Optional[dict] = None
    context: Optional[list] = None


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    translator = translator_mir_en if request.direction == "mir_to_en" else translator_en_mir
    if translator is None:
        raise HTTPException(status_code=503, detail=f"Translator not initialized for direction {request.direction}")

    try:
        if request.direction == "mir_to_en":
            prediction = translator(mirad_text=request.text)
            translation = prediction.english_text
        else:
            prediction = translator(english_text=request.text)
            translation = prediction.mirad_text

        response = TranslateResponse(
            text=request.text,
            translation=translation,
            direction=request.direction,
            confidence=str(getattr(prediction, 'confidence', 'N/A')),
        )

        # Include retrieval details when requested
        if request.retrieve:
            response.word_equivalents = getattr(prediction, 'word_equivalents', None)
            response.context = getattr(prediction, 'context', None)

        return response
    except Exception as e:
        logging.error("Translation failed: %s", str(e))
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))