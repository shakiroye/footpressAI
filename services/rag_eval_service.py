"""
Évaluation du RAG — Option Bonus
----------------------------------
Mesure la qualité des réponses RAG sur 3 dimensions :

1. Faithfulness   : la réponse est-elle ancrée dans les chunks récupérés ?
2. Relevance      : la réponse répond-elle vraiment à la question ?
3. Completeness   : les chunks contenaient-ils assez d'info pour répondre ?

Approche : GPT-4o évalue lui-même (self-evaluation) — simple mais efficace
pour un MVP. En production : utiliser RAGAS avec des métriques automatisées.
"""

from services.openai_service import generate


async def evaluate_rag_response(
    question: str,
    answer: str,
    chunks: list[str]
) -> dict:
    """
    Évalue une réponse RAG sur 3 critères.
    Retourne un score sur 10 pour chaque critère + verdict global.
    """

    context = "\n---\n".join(chunks) if chunks else "Aucun chunk fourni"

    prompt = f"""Tu es un évaluateur expert de systèmes RAG (Retrieval-Augmented Generation).
Évalue la réponse suivante selon 3 critères stricts. Réponds UNIQUEMENT avec le format demandé.

QUESTION POSÉE :
{question}

CHUNKS RÉCUPÉRÉS (contexte) :
{context}

RÉPONSE GÉNÉRÉE :
{answer}

---
Évalue chaque critère de 0 à 10 :

1. FAITHFULNESS (0-10) : La réponse s'appuie-t-elle UNIQUEMENT sur les chunks ?
   (0 = hallucinations totales, 10 = 100% ancré dans les chunks)

2. RELEVANCE (0-10) : La réponse répond-elle directement à la question ?
   (0 = hors sujet, 10 = répond parfaitement)

3. COMPLETENESS (0-10) : Les chunks contenaient-ils assez d'info pour répondre ?
   (0 = chunks inutiles, 10 = chunks très pertinents)

Format de réponse OBLIGATOIRE :
FAITHFULNESS: [score]/10 | [justification courte]
RELEVANCE: [score]/10 | [justification courte]
COMPLETENESS: [score]/10 | [justification courte]
SCORE_GLOBAL: [moyenne]/10
VERDICT: [EXCELLENT / BON / MOYEN / INSUFFISANT]
PROBLEME_PRINCIPAL: [si score < 7, décrire le problème principal]"""

    eval_result = await generate(prompt=prompt)

    # Parse les scores
    scores = _parse_scores(eval_result)

    return {
        "question": question,
        "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
        "nb_chunks_evaluated": len(chunks),
        "scores": scores,
        "raw_evaluation": eval_result,
        "interpretation": _interpret(scores.get("global", 0))
    }


def _parse_scores(raw: str) -> dict:
    """Extrait les scores numériques de la réponse GPT."""
    scores = {}
    lines = raw.upper().split("\n")

    for line in lines:
        if "FAITHFULNESS:" in line:
            scores["faithfulness"] = _extract_score(line)
        elif "RELEVANCE:" in line:
            scores["relevance"] = _extract_score(line)
        elif "COMPLETENESS:" in line:
            scores["completeness"] = _extract_score(line)
        elif "SCORE_GLOBAL:" in line:
            scores["global"] = _extract_score(line)

    # Calcul manuel si score global absent
    if "global" not in scores and len(scores) == 3:
        vals = [v for v in scores.values() if v is not None]
        scores["global"] = round(sum(vals) / len(vals), 1) if vals else None

    return scores


def _extract_score(line: str) -> float | None:
    """Extrait le premier nombre d'une ligne."""
    import re
    match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', line)
    if match:
        return float(match.group(1))
    return None


def _interpret(score: float | None) -> str:
    if score is None:
        return "Score non calculable"
    if score >= 8:
        return "EXCELLENT — Le RAG répond fidèlement grâce aux données"
    if score >= 6:
        return "BON — Quelques imprécisions mineures"
    if score >= 4:
        return "MOYEN — Le modèle complète avec ses connaissances propres"
    return "INSUFFISANT — Réponse peu fiable, vérifier les chunks indexés"
