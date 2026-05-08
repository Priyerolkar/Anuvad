"""
Smoke tests for Anuvad.

These tests download the IndicTrans2 model on first run (~1 GB), so they're slow
the first time. Run with:
    pytest tests/ -v

Mark slow tests if you want to skip them in CI:
    pytest tests/ -v -m "not slow"
"""

from __future__ import annotations

import pytest

from api.translator import SUPPORTED_LANGUAGES, Translator, get_translator


def test_supported_languages_present():
    assert "marathi" in SUPPORTED_LANGUAGES
    assert "hindi" in SUPPORTED_LANGUAGES
    assert SUPPORTED_LANGUAGES["marathi"] == "mar_Deva"


def test_get_translator_is_singleton():
    t1 = get_translator()
    t2 = get_translator()
    assert t1 is t2, "get_translator should return the cached instance"


@pytest.mark.slow
def test_translate_marathi():
    t = get_translator()
    result = t.translate("The engine runs smoothly.", target_lang="marathi")
    assert result.translated_text.strip() != ""
    assert result.target_lang == "mar_Deva"
    assert result.latency_ms > 0


@pytest.mark.slow
def test_translate_batch():
    t = get_translator()
    sentences = [
        "The piston moves up and down inside the cylinder.",
        "Heat transfer occurs through conduction, convection, and radiation.",
    ]
    results = t.translate_batch(sentences, target_lang="hindi")
    assert len(results) == 2
    for r in results:
        assert r.translated_text.strip() != ""
        assert r.target_lang == "hin_Deva"


def test_translate_rejects_empty():
    t = Translator.__new__(Translator)  # bypass __init__ to test validation only
    with pytest.raises(ValueError):
        Translator.translate(t, "", target_lang="marathi")


def test_translate_rejects_unknown_language():
    t = Translator.__new__(Translator)
    with pytest.raises(ValueError):
        Translator.translate(t, "hello", target_lang="klingon")  # type: ignore[arg-type]
