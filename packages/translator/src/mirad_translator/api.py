"""
FastAPI translation endpoint.
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Mirad Translator API"}

@app.post("/translate")
async def translate(text: str):
    # Will use TranslateEnToMirad
    return {"text": text, "translation": "Translated text"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
