"""UI de démo jetable : pose une question, affiche la réponse + citations.

Usage:
    uv sync --extra ui
    uv run streamlit run streamlit_app/app.py
"""

import streamlit as st

from rip_agent.rag.pipeline import RAGPipeline


@st.cache_resource
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


st.title("RIP-Agent — démo")

question = st.text_input("Question sur le corpus DSP/RIP")

if st.button("Répondre") and question:
    with st.spinner("Recherche en cours..."):
        answer = get_pipeline().answer(question)

    if answer.refused:
        st.warning(answer.text)
    else:
        st.write(answer.text)
        if answer.citations:
            st.subheader("Citations")
            for citation in answer.citations:
                section = f" — {citation.source_section}" if citation.source_section else ""
                st.caption(f"[{citation.chunk_id}] {citation.source_doc}{section}")
