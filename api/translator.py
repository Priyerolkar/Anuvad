"""
Anuvad core translation module (no IndicTransToolkit dependency).

Wraps IndicTrans2 (AI4Bharat) for English -> Indian language translation
using only `transformers` + `sacremoses`. Implements the minimal pre/post-
processing IndicTrans2 expects:

    - Source-side tokenization with Moses (English).
    - Target-language tag prepended to each input.
    - Detokenization on the output.

This avoids the Cython-compiled IndicTransToolkit and works on any Windows
machine without C++ build tools. Translation quality is identical -- the
toolkit only handled preprocessing.

References:
- IndicTrans2 paper: https://arxiv.org/abs/2305.16307
- Model card: https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import torch
from sacremoses import MosesPunctNormalizer, MosesTokenizer, MosesDetokenizer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)

# Supported target languages for English -> Indic.
SUPPORTED_LANGUAGES: dict[str, str] = {
    "marathi": "mar_Deva",
    "hindi": "hin_Deva",
    "tamil": "tam_Taml",
    "bengali": "ben_Beng",
    "telugu": "tel_Telu",
    "gujarati": "guj_Gujr",
    "kannada": "kan_Knda",
}

LangName = Literal[
    "marathi", "hindi", "tamil", "bengali", "telugu", "gujarati", "kannada"
]

DEFAULT_MODEL = "ai4bharat/indictrans2-en-indic-dist-200M"
SOURCE_LANG = "eng_Latn"


@dataclass
class TranslationResult:
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    latency_ms: float
    model_name: str


def _preprocess_english(text: str, normalizer: MosesPunctNormalizer,
                        tokenizer: MosesTokenizer) -> str:
    """Normalize punctuation and Moses-tokenize an English sentence."""
    text = normalizer.normalize(text.strip())
    return tokenizer.tokenize(text, return_str=True, escape=False)


def _postprocess_indic(text: str, detokenizer: MosesDetokenizer) -> str:
    """Detokenize the model's output to a clean target-language string."""
    return detokenizer.detokenize(text.split())


class Translator:
    """English -> Indian language translator powered by IndicTrans2."""

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str | None = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Loading %s on %s ...", model_name, self.device)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, trust_remote_code=True
        ).to(self.device)
        self.model.eval()

        # Moses utilities for English source side.
        self.en_normalizer = MosesPunctNormalizer(lang="en")
        self.en_tokenizer = MosesTokenizer(lang="en")
        # Detokenizer is language-agnostic for Indic scripts in practice.
        self.detokenizer = MosesDetokenizer(lang="hi")

        logger.info("Translator ready.")

    def translate(
        self,
        text: str,
        target_lang: LangName = "marathi",
        source_lang: str = SOURCE_LANG,
        max_length: int = 256,
    ) -> TranslationResult:
        if not text or not text.strip():
            raise ValueError("Input text is empty.")
        if target_lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{target_lang}'. "
                f"Choose from: {list(SUPPORTED_LANGUAGES)}"
            )
        return self.translate_batch(
            [text], target_lang=target_lang, source_lang=source_lang, max_length=max_length
        )[0]

    def translate_batch(
        self,
        texts: list[str],
        target_lang: LangName = "marathi",
        source_lang: str = SOURCE_LANG,
        max_length: int = 256,
        batch_size: int = 8,
    ) -> list[TranslationResult]:
        if target_lang not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{target_lang}'. "
                f"Choose from: {list(SUPPORTED_LANGUAGES)}"
            )
        target_code = SUPPORTED_LANGUAGES[target_lang]

        results: list[TranslationResult] = []
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            t0 = time.perf_counter()

            # IndicTrans2 expects each line as: "<src_lang> <tgt_lang> <tokenized text>"
            preprocessed = [
                f"{source_lang} {target_code} "
                + _preprocess_english(t, self.en_normalizer, self.en_tokenizer)
                for t in chunk
            ]

            inputs = self.tokenizer(
                preprocessed,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                max_length=max_length,
            ).to(self.device)

            with torch.inference_mode():
                generated = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=max_length,
                    num_beams=5,
                    num_return_sequences=1,
                )

            decoded = self.tokenizer.batch_decode(
                generated.detach().cpu().tolist(),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            translations = [_postprocess_indic(d, self.detokenizer) for d in decoded]

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            per_item_ms = elapsed_ms / len(chunk)

            for src, tgt in zip(chunk, translations):
                results.append(
                    TranslationResult(
                        source_text=src,
                        translated_text=tgt,
                        source_lang=source_lang,
                        target_lang=target_code,
                        latency_ms=per_item_ms,
                        model_name=self.model_name,
                    )
                )

        return results


@lru_cache(maxsize=1)
def get_translator(model_name: str = DEFAULT_MODEL) -> Translator:
    """Return a process-wide singleton translator. Cached so the model loads once."""
    return Translator(model_name=model_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    t = get_translator()
    sample = "The heat exchanger transfers thermal energy between two fluids."
    out = t.translate(sample, target_lang="marathi")
    print(f"EN: {out.source_text}")
    print(f"MR: {out.translated_text}")
    print(f"Latency: {out.latency_ms:.1f} ms")