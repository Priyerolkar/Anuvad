"""
FastAPI backend for Anuvad.

Endpoints:
    GET  /            -> service info
    GET  /health      -> health check
    GET  /languages   -> supported target languages
    POST /translate   -> translate one string
    POST /translate/batch -> translate a list of strings

Run locally:
    uvicorn api.main:app --reload --port 8000

Then visit http://localhost:8000/docs for the interactive Swagger UI.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.translator import (
    SUPPORTED_LANGUAGES,
    LangName,
    TranslationResult,
    get_translator,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Pydantic schemas ----------


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="English text to translate.")
    target_lang: LangName = Field("marathi", description="Target Indian language.")


class BatchTranslateRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=64)
    target_lang: LangName = Field("marathi")


class TranslateResponse(BaseModel):
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    latency_ms: float
    model_name: str

    @classmethod
    def from_result(cls, r: TranslationResult) -> "TranslateResponse":
        return cls(
            source_text=r.source_text,
            translated_text=r.translated_text,
            source_lang=r.source_lang,
            target_lang=r.target_lang,
            latency_ms=round(r.latency_ms, 2),
            model_name=r.model_name,
        )


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_loaded: bool
    model_name: str


# ---------- App lifespan: warm the model on startup ----------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Warming up translator (this may take ~30s on first run)...")
    get_translator()
    logger.info("Translator ready.")
    yield


app = FastAPI(
    title="Anuvad",
    description="English → Indian language translator for engineering content. Powered by IndicTrans2.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the Streamlit frontend (and Hugging Face Spaces) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Routes ----------


@app.get("/")
def root():
    return {
        "service": "Anuvad",
        "description": "English → Indian language translator for engineering content.",
        "docs": "/docs",
        "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
    }


@app.get("/health", response_model=HealthResponse)
def health():
    t = get_translator()
    return HealthResponse(status="ok", model_loaded=True, model_name=t.model_name)


@app.get("/languages")
def languages():
    return {"languages": SUPPORTED_LANGUAGES}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    try:
        result = get_translator().translate(req.text, target_lang=req.target_lang)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover -- model errors
        logger.exception("Translation failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    return TranslateResponse.from_result(result)


@app.post("/translate/batch", response_model=list[TranslateResponse])
def translate_batch(req: BatchTranslateRequest):
    try:
        results = get_translator().translate_batch(req.texts, target_lang=req.target_lang)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("Batch translation failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    return [TranslateResponse.from_result(r) for r in results]
