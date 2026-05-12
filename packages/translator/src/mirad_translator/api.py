from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import traceback

from mirad_translator.translate import TranslatorModule
from mirad_translator.ollama_lm import OllamaLM
import dspy

logger = logging.getLogger(__name__)

app = FastAPI()

# Global translator instance — initialized lazily
translator = None


@app.on_event("startup")
async def startup_event():
    global translator
    try:
        lm = OllamaLM()
        dspy.configure(lm=lm)
        translator = TranslatorModule()
        logger.info("Translator initialized successfully")
    except Exception as e:
        logger.warning(
            "Translator initialization deferred: %s. "
            "Health endpoint will report unhealthy until Ollama is available.",
            e,
        )

@app.get("/")
async def root():
    return {"message": "Mirad Translator API"}

@app.get("/health")
async def health():
    if translator is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "Translator not initialized"}
        )
    try:
        # Test translator is working
        result = translator.forward(english_text="test")
        if not result.mirad_text:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "unhealthy", "reason": "Translator returned empty result"}
            )
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "Translator health check failed"}
        )
    
    return {"status": "healthy"}

class TranslateRequest(BaseModel):
    text: str

@app.post("/translate")
async def translate(request: TranslateRequest):
    if translator is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")
    
    try:
        prediction = translator.forward(english_text=request.text)
        return {
            "text": request.text,
            "translation": prediction.mirad_text,
            "confidence": prediction.confidence
        }
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
