"""Anuvad — Streamlit UI for engineering translation."""

import streamlit as st
from api.translator import get_translator, SUPPORTED_LANGUAGES

st.set_page_config(
    page_title="Anuvad — Engineering Translator",
    page_icon="🌐",
    layout="centered",
)

st.title("🌐 Anuvad")
st.caption("Engineering content translator — English → Indian languages")
st.markdown(
    "Built on **IndicTrans2** (AI4Bharat). Optimized for technical and "
    "engineering vocabulary. [GitHub](https://github.com/Priyerolkar/Anuvad)"
)

with st.sidebar:
    st.header("About")
    st.write(
        "Anuvad translates English engineering content into Indian languages. "
        "Best for technical manuals, engineering documentation, and educational content."
    )
    st.markdown("---")
    st.write("**Built by Priyanka Yerolkar**")
    st.write("Mechanical engineer building AI.")
    st.markdown("[LinkedIn](https://linkedin.com/in/priyankayerolkar)")


@st.cache_resource(show_spinner="Loading IndicTrans2 model (one-time, ~2 min)...")
def load_translator():
    return get_translator()


translator = load_translator()

col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_area(
        "English text",
        value="The heat exchanger transfers thermal energy between two fluids.",
        height=140,
    )
with col2:
    target_lang = st.selectbox(
        "Translate to",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
    )

if st.button("Translate", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Please enter some English text.")
    else:
        with st.spinner("Translating..."):
            result = translator.translate(text, target_lang=target_lang)
        st.success("Done")
        st.markdown(f"### {target_lang.title()}")
        st.markdown(f"### {result.translated_text}")
        st.caption(f"Latency: {result.latency_ms:.0f} ms · Model: {result.model_name}")

st.markdown("---")
st.markdown("**Try these engineering examples:**")
examples = [
    "Tighten the bolt to a torque of 25 Newton-meters.",
    "The deep drawing process forms sheet metal into cylindrical parts.",
    "Check the coolant level before starting the engine.",
    "The CNC machine operates with a feed rate of 200 millimeters per minute.",
]
cols = st.columns(2)
for i, ex in enumerate(examples):
    if cols[i % 2].button(ex, key=f"ex_{i}"):
        with st.spinner("Translating example..."):
            result = translator.translate(ex, target_lang=target_lang)
        st.markdown(f"**EN:** {ex}")
        st.markdown(f"**{target_lang.title()}:** {result.translated_text}")
