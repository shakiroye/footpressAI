"""
Router Pipeline — Défi 3
-------------------------
POST /api/v1/pipeline/generate-article   → notes brutes → article structuré
POST /api/v1/pipeline/check-coherence    → détection d'incohérences
POST /api/v1/pipeline/synthesize         → synthèse multi-sources
"""

from fastapi import APIRouter, Form, HTTPException
from typing import Optional, List

from services import pipeline_service

router = APIRouter(prefix="/pipeline", tags=["Défi 3 - Pipeline Complet"])


@router.post("/generate-article")
async def generate_article(
    notes: str = Form(..., description="Notes brutes du journaliste"),
    use_rag: bool = Form(True, description="Enrichir avec les archives indexées")
):
    """
    Pipeline complet : notes brutes → article de presse structuré.

    Étapes automatiques :
    1. Extraction des entités (joueurs, clubs, événements)
    2. Enrichissement contextuel via RAG (si archives disponibles)
    3. Génération d'un article structuré avec GPT-4o

    Exemple de notes : "PSG 2-1 Bayern. Mbappé doublé (23', 67').
    Kane réduit score 81'. Donnarumma 7 arrêts. Possession PSG 48%."
    """
    if not notes.strip():
        raise HTTPException(status_code=400, detail="Les notes ne peuvent pas être vides.")

    result = await pipeline_service.generate_article(notes, use_rag=use_rag)
    return result


@router.post("/check-coherence")
async def check_coherence(
    article: str = Form(..., description="Article rédigé à vérifier"),
    stats: str = Form(..., description="Statistiques officielles de référence")
):
    """
    Détecte les incohérences entre un article rédigé et les stats officielles.

    Identifie :
    - Erreurs sur les scores, buteurs, minutes
    - Statistiques incorrectes (possession, tirs, passes)
    - Noms de joueurs ou clubs erronés
    - Approximations trompeuses

    Retourne un rapport de fact-checking avec niveau de gravité.
    """
    if not article.strip() or not stats.strip():
        raise HTTPException(
            status_code=400,
            detail="L'article et les statistiques sont requis."
        )

    result = await pipeline_service.check_coherence(article, stats)
    return result


@router.post("/synthesize")
async def synthesize(
    question: str = Form(..., description="Question à poser sur les archives"),
    sources: str = Form(..., description="Noms des fichiers séparés par des virgules")
):
    """
    Synthèse multi-sources : interroge plusieurs archives et croise les données.

    Permet au journaliste de :
    - Suivre la progression d'un joueur sur plusieurs matchs
    - Comparer les performances d'une équipe sur une saison
    - Détecter des tendances à travers plusieurs rapports

    Exemple :
    - question: "Quelle est l'évolution de Mbappé sur ces matchs ?"
    - sources: "match_psg_bayern.pdf,match_psg_real.pdf,match_psg_city.pdf"
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")

    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    if not source_list:
        raise HTTPException(status_code=400, detail="Au moins une source est requise.")

    if len(source_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 sources par synthèse.")

    result = await pipeline_service.synthesize_sources(question, source_list)
    return result
