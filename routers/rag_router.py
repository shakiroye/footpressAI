"""
Router RAG — Défi 2
--------------------
POST /api/v1/rag/upload       → ingère un PDF dans le pipeline RAG
POST /api/v1/rag/query        → interroge les archives avec recherche vectorielle
POST /api/v1/rag/compare      → compare deux documents indexés
POST /api/v1/rag/evaluate     → évalue la qualité d'une réponse RAG [BONUS]
GET  /api/v1/rag/files        → liste les fichiers uploadés
DELETE /api/v1/rag/files/{f}  → supprime un fichier
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional

from services import blob_service, rag_service
from services.rag_eval_service import evaluate_rag_response
from security.api_key import optional_api_key

router = APIRouter(prefix="/rag", tags=["Défi 2 - RAG Archives"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(optional_api_key)
):
    """
    Upload un PDF dans le Blob Storage et l'indexe dans Azure AI Search.
    Pipeline : PDF → extraction texte → chunking → embedding → index vectoriel.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    content = await file.read()

    if len(content) > 10 * 1024 * 1024:  # 10 MB max
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 MB).")

    # Préfixe par utilisateur pour isolation multi-utilisateurs
    scoped_filename = f"{user_id}/{file.filename}" if user_id != "anonymous" else file.filename

    # 1. Upload dans le Blob Storage
    blob_result = await blob_service.upload_file(scoped_filename, content)
    if not blob_result.get("success"):
        raise HTTPException(status_code=500, detail=f"Erreur Blob Storage : {blob_result.get('error')}")

    # 2. Ingestion dans l'index RAG
    rag_result = await rag_service.ingest_pdf(content, scoped_filename)

    return {
        "upload": blob_result,
        "indexation": rag_result,
        "user": user_id
    }


@router.post("/query")
async def query_archives(
    question: str = Form(...),
    source: Optional[str] = Form(None)
):
    """
    Interroge les archives du journaliste avec recherche vectorielle.
    Répond UNIQUEMENT à partir des documents uploadés (pas d'hallucination).

    Exemples :
    - "Comment Mbappé a performé dans les derbies ?"
    - "Quels sont les stats de possession du PSG cette saison ?"
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")

    result = await rag_service.query_rag(question, source_filter=source)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/compare")
async def compare_documents(
    source1: str = Form(...),
    source2: str = Form(...),
    aspect: Optional[str] = Form(None)
):
    """
    Compare deux documents indexés sur un aspect donné.
    Exemple : comparer les performances d'un joueur dans deux rapports de match.
    """
    if source1 == source2:
        raise HTTPException(status_code=400, detail="Les deux sources doivent être différentes.")

    result = await rag_service.compare_documents(source1, source2, aspect or "")

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/evaluate")
async def evaluate_rag(
    question: str = Form(...),
    answer: str = Form(...),
    chunks: str = Form(..., description="Chunks utilisés séparés par |||")
):
    """
    [BONUS] Évalue la qualité d'une réponse RAG.

    Scores retournés :
    - Faithfulness  : la réponse est-elle ancrée dans les chunks ? (0-10)
    - Relevance     : répond-elle à la question ? (0-10)
    - Completeness  : les chunks étaient-ils suffisants ? (0-10)
    - Score global  : moyenne des 3 critères

    Workflow typique :
    1. POST /rag/query → récupérer question + answer + chunks
    2. POST /rag/evaluate → évaluer la qualité de la réponse
    """
    chunk_list = [c.strip() for c in chunks.split("|||") if c.strip()]
    result = await evaluate_rag_response(question, answer, chunk_list)
    return result


@router.get("/files")
async def list_files():
    """Liste tous les fichiers uploadés dans le Blob Storage."""
    return {"files": await blob_service.list_files()}


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Supprime un fichier du Blob Storage."""
    result = await blob_service.delete_file(filename)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result
