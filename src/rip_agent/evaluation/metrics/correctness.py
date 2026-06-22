from rip_agent.evaluation.judge import JudgeClient

_SYSTEM_PROMPT = (
    "Tu es un juge qui évalue si une réponse générée est correcte par rapport "
    "à une réponse de référence. Réponds uniquement par un score entre 0 et 1 "
    "(0 = incorrecte, 1 = correcte), sans aucun texte additionnel."
)


def build_correctness_prompt(question: str, ground_truth: str, answer_text: str) -> list[dict[str, str]]:
    user_prompt = (
        f"Question : {question}\n"
        f"Réponse de référence : {ground_truth}\n"
        f"Réponse générée : {answer_text}\n"
        "Score :"
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def compute_correctness(question: str, ground_truth: str, answer_text: str, judge: JudgeClient) -> float:
    messages = build_correctness_prompt(question, ground_truth, answer_text)
    return judge.score(messages)
