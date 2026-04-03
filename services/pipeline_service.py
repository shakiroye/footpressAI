"""
Pipeline complet — Défi 3
--------------------------
Use case FootPress AI :

1. generate_article  : notes brutes → enrichissement RAG → article structuré
2. check_coherence   : article rédigé + stats → détection d'incohérences
3. synthesize        : question → synthèse multi-sources depuis les archives
"""

from services.openai_service import generate
from services.text_service import extract_entities, analyze_sentiment
from services.rag_service import query_rag


# ── 1. Génération d'article enrichi ───────────────────────────────────────
async def generate_article(raw_notes: str, use_rag: bool = True) -> dict:
    """
    Pipeline : notes brutes du journaliste
    → extraction d'entités (joueurs, clubs, scores)
    → enrichissement contextuel via RAG (archives)
    → génération d'un article de presse structuré
    """

    # Étape 1 — Extraction d'entités pour identifier les sujets clés
    entities_result = await extract_entities(raw_notes)
    entities = entities_result.get("entities", [])

    persons  = [e["text"] for e in entities if e["category"] == "Person"]
    orgs     = [e["text"] for e in entities if e["category"] == "Organization"]
    events   = [e["text"] for e in entities if e["category"] == "Event"]

    # Étape 2 — Enrichissement RAG (recherche dans les archives du journaliste)
    rag_context = ""
    if use_rag and (persons or orgs):
        rag_query = f"Performances et historique de {', '.join(persons[:3] + orgs[:2])}"
        rag_result = await query_rag(rag_query)
        if "answer" in rag_result and "Aucune donnée" not in rag_result["answer"]:
            rag_context = rag_result["answer"]
            rag_sources = rag_result.get("sources_used", [])
        else:
            rag_sources = []
    else:
        rag_sources = []

    # Étape 3 — Génération de l'article structuré
    context_block = f"\n\nContexte issu des archives :\n{rag_context}" if rag_context else ""

    prompt = f"""Tu es un journaliste sportif senior. Transforme ces notes brutes en un article de presse structuré et professionnel.

Notes brutes :
{raw_notes}

Entités détectées :
- Joueurs : {', '.join(persons) if persons else 'non identifiés'}
- Clubs/Orgs : {', '.join(orgs) if orgs else 'non identifiés'}
- Événements : {', '.join(events) if events else 'non identifiés'}
{context_block}

Structure l'article avec :
1. Un titre accrocheur
2. Un chapeau (2-3 phrases résumant l'essentiel)
3. Le corps de l'article (3-4 paragraphes)
4. Une conclusion avec perspective

Sois factuel, ne génère que ce qui est appuyé par les notes ou le contexte fourni."""

    article = await generate(prompt=prompt)

    return {
        "article": article,
        "pipeline_steps": {
            "entities_extracted": {
                "persons": persons,
                "organizations": orgs,
                "events": events
            },
            "rag_enrichment": {
                "used": use_rag and bool(rag_context),
                "sources": rag_sources,
                "context_preview": rag_context[:200] + "..." if len(rag_context) > 200 else rag_context
            }
        }
    }


# ── 2. Détection d'incohérences ────────────────────────────────────────────
async def check_coherence(article: str, stats: str) -> dict:
    """
    Compare un article rédigé avec des statistiques officielles.
    Détecte les incohérences, erreurs factuelles et approximations.

    Exemples d'incohérences détectées :
    - "Mbappé a marqué 3 buts" alors que les stats disent 2
    - "Possession 60% PSG" alors que les stats disent 48%
    - Nom de joueur incorrect
    """

    prompt = f"""Tu es un fact-checker spécialisé dans le journalisme sportif.

Analyse l'article ci-dessous et compare-le aux statistiques officielles fournies.
Identifie TOUTES les incohérences, erreurs factuelles et approximations.

ARTICLE RÉDIGÉ :
{article}

STATISTIQUES OFFICIELLES :
{stats}

Pour chaque incohérence trouvée, fournis :
1. La phrase de l'article concernée
2. Ce qui est incorrect
3. La valeur correcte selon les stats
4. Niveau de gravité : [CRITIQUE / MAJEURE / MINEURE]

Si aucune incohérence : réponds "Aucune incohérence détectée — l'article est conforme aux statistiques."

Format de réponse structuré en JSON-like :
INCOHÉRENCES TROUVÉES : [nombre]
---
[Pour chaque incohérence]
Phrase : "..."
Problème : ...
Correction : ...
Gravité : ...
---
VERDICT GLOBAL : ..."""

    result = await generate(prompt=prompt)

    # Analyse du sentiment pour évaluer le ton de l'article
    sentiment = await analyze_sentiment(article)

    return {
        "coherence_report": result,
        "article_sentiment": sentiment.get("sentiment", "unknown"),
        "article_sentiment_scores": sentiment.get("scores", {}),
        "stats_provided": stats[:300] + "..." if len(stats) > 300 else stats
    }


# ── 3. Synthèse multi-sources ──────────────────────────────────────────────
async def synthesize_sources(question: str, sources: list[str]) -> dict:
    """
    Interroge plusieurs sources archivées et produit une synthèse cohérente.
    Permet au journaliste de croiser plusieurs rapports de matchs ou articles.

    Ex : "Quelle est la progression de Mbappé sur les 3 derniers matchs ?"
    """

    source_answers = {}
    all_chunks = []

    for source in sources:
        result = await query_rag(question, source_filter=source)
        if "answer" in result and "Aucune donnée" not in result["answer"]:
            source_answers[source] = result["answer"]
            all_chunks.extend(result.get("sources_used", []))

    if not source_answers:
        return {
            "question": question,
            "synthesis": "Aucune donnée pertinente trouvée dans les sources spécifiées.",
            "sources_consulted": sources,
            "individual_answers": {}
        }

    # Construction du prompt de synthèse
    sources_block = "\n\n".join(
        f"=== {src} ===\n{answer}"
        for src, answer in source_answers.items()
    )

    prompt = f"""Tu es un journaliste sportif. Produis une synthèse journalistique à partir de ces différentes sources.

Question : {question}

{sources_block}

Ta synthèse doit :
1. Répondre directement à la question
2. Croiser et comparer les informations des différentes sources
3. Mettre en évidence les tendances ou évolutions
4. Citer les sources utilisées
5. Signaler toute contradiction entre les sources

Sois factuel et sourcé. Ne génère pas d'informations absentes des extraits."""

    synthesis = await generate(prompt=prompt)

    return {
        "question": question,
        "synthesis": synthesis,
        "sources_consulted": list(source_answers.keys()),
        "sources_without_data": [s for s in sources if s not in source_answers],
        "individual_answers": source_answers,
        "total_chunks_used": len(all_chunks)
    }
