from rip_agent.schemas.retrieval import RetrievedChunk

REFUSAL_PREFIX = "REFUS:"

_SYSTEM_PROMPT = f"""Tu es un assistant qui répond à des questions sur des contrats de délégation \
de service public (DSP) télécom, en te basant UNIQUEMENT sur le contexte fourni.

Règles strictes :
- N'utilise aucune connaissance extérieure au contexte fourni.
- Cite la source de chaque affirmation en indiquant l'identifiant du chunk entre crochets, \
par exemple [chunk_id].
- Si le contexte ne permet pas de répondre à la question, réponds exactement \
"{REFUSAL_PREFIX} le contexte ne contient pas l'information demandée." et rien d'autre.
"""


def build_answer_prompt(question: str, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"[{result.chunk.id}] (section: {result.chunk.section_title or 'N/A'})\n{result.chunk.text}"
        for result in chunks
    )

    user_prompt = f"Contexte :\n{context}\n\nQuestion : {question}"

    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
