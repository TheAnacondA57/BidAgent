from rip_agent.evaluation.judge import JudgeClient
from rip_agent.schemas.retrieval import RetrievedChunk

_SYSTEM_PROMPT = (
    "Tu es un juge qui évalue si une réponse est fidèle à son contexte, "
    "c'est-à-dire qu'elle n'affirme rien qui ne soit pas soutenu par le "
    "contexte fourni. Réponds uniquement par un score entre 0 et 1 "
    "(0 = invente des informations, 1 = entièrement fondée sur le contexte), "
    "sans aucun texte additionnel."
)


def build_faithfulness_prompt(answer_text: str, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    context = "\n\n".join(f"[{result.chunk.id}] {result.chunk.text}" for result in chunks)
    user_prompt = f"Contexte :\n{context}\n\nRéponse à évaluer : {answer_text}\nScore :"
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def compute_faithfulness(answer_text: str, chunks: list[RetrievedChunk], judge: JudgeClient) -> float:
    messages = build_faithfulness_prompt(answer_text, chunks)
    return judge.score(messages)
