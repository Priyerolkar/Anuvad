"""
Streamlit frontend for Anuvad.

Run locally:
    streamlit run app.py

This UI calls the translator module directly so it works as a single-process
deployment on Hugging Face Spaces. If you want it to call the FastAPI backend
instead, set USE_API=true and API_URL=<your-api-url> as environment variables.
"""

from __future__ import annotations

import os
import time

import streamlit as st

# ---------- Page config ----------

st.set_page_config(
    page_title="Anuvad — Engineering Translator",
    page_icon="🌐",
    layout="centered",
)

USE_API = os.environ.get("USE_API", "false").lower() == "true"
API_URL = os.environ.get("API_URL", "http://localhost:8000")


# ---------- Translation helpers ----------

@st.cache_resource(show_spinner="Loading IndicTrans2 model (first run takes ~30s)...")
def load_translator():
    from api.translator import get_translator
    return get_translator()


def translate_local(text: str, target_lang: str) -> dict:
    translator = load_translator()
    result = translator.translate(text, target_lang=target_lang)
    return {
        "translated_text": result.translated_text,
        "latency_ms": result.latency_ms,
        "model_name": result.model_name,
    }


def translate_via_api(text: str, target_lang: str) -> dict:
    import requests
    resp = requests.post(
        f"{API_URL}/translate",
        json={"text": text, "target_lang": target_lang},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def translate(text: str, target_lang: str) -> dict:
    return translate_via_api(text, target_lang) if USE_API else translate_local(text, target_lang)


# ---------- UI ----------

st.title("🌐 Anuvad")
st.caption("**Engineering content translator — English → Marathi · Hindi · and more**")

with st.expander("ℹ️ About this project"):
    st.markdown(
        """
        Anuvad translates technical engineering content from English into Indian
        languages. It's optimized for engineering documentation, technical
        manuals, and educational coursework — domains where generic translators
        often lose precision.

        **Model:** IndicTrans2 (AI4Bharat, IIT Madras)
        **Backend:** FastAPI · **Frontend:** Streamlit

        Built by [Priyanka Yerolkar](https://github.com/Priyerolkar) — a
        mechanical and automotive engineer building AI for industrial problems.
        Inspired by translation work for NPTEL (IIT Kharagpur).
        """
    )

LANGUAGES = ["marathi", "hindi", "tamil", "bengali", "telugu", "gujarati", "kannada"]

col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_area(
        "English text",
        height=180,
        placeholder="The heat exchanger transfers thermal energy between two fluids without mixing them.",
    )
with col2:
    target = st.selectbox("Target language", LANGUAGES, index=0)
    st.write("")
    go = st.button("Translate", type="primary", use_container_width=True)

# Sample sentences make demos easy and show the engineering focus.
st.markdown("**Try a sample:**")
samples = [
    "The heat exchanger transfers thermal energy between two fluids.",
    "Increase the feed rate to reduce machining time, but watch tool wear.",
    "Tolerance stack-up analysis ensures parts assemble correctly.",
    "The deep drawing process forms sheet metal into cup-shaped components.",
]
sample_cols = st.columns(len(samples))
for i, s in enumerate(samples):
    if sample_cols[i].button(f"Sample {i+1}", key=f"sample-{i}", help=s):
        st.session_state["text_input"] = s
        text = s
        go = True

if go:
    if not text or not text.strip():
        st.warning("Please enter some text.")
    else:
        try:
            t0 = time.perf_counter()
            result = translate(text, target)
            wall_ms = (time.perf_counter() - t0) * 1000

            st.success("Translation complete.")
            st.markdown(f"### {target.title()}")
            st.markdown(
                f"<div style='font-size:1.25rem; line-height:1.6'>"
                f"{result['translated_text']}</div>",
                unsafe_allow_html=True,
            )

            metrics = st.columns(3)
            metrics[0].metric("Model latency", f"{result['latency_ms']:.0f} ms")
            metrics[1].metric("Total round-trip", f"{wall_ms:.0f} ms")
            metrics[2].metric("Characters", len(text))

            with st.expander("Details"):
                st.json(result)
        except Exception as e:
            st.error(f"Translation failed: {e}")

st.divider()
st.caption(
    "Open source · MIT license · "
    "[GitHub](https://github.com/Priyerolkar/Anuvad)"
)
