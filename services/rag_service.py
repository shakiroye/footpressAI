"""
Pipeline RAG pour FootPress AI
-------------------------------
ingestion → chunking → embedding → indexation → requêtage

Use case : le journaliste uploade ses archives (anciens articles,
rapports de matchs, fiches joueurs) et interroge ses propres données.
"""

import io
import re
import uuid
from typing import Optional

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

from config import settings
from services.openai_service import embed, generate

# ── Clients Azure AI Search ────────────────────────────────────────────────
_credential = AzureKeyCredential(settings.azure_search_key)

_index_client = SearchIndexClient(
    endpoint=settings.azure_search_endpoint,
    credential=_credential
)

_search_client = SearchClient(
    endpoint=settings.azure_search_endpoint,
    index_name=settings.azure_search_index,
    credential=_credential
)

# ── Constantes ─────────────────────────────────────────────────────────────
CHUNK_SIZE = 400        # mots par chunk
CHUNK_OVERLAP = 50      # mots de chevauchement
TOP_K = 5               # chunks récupérés par requête
VECTOR_DIMS = 1536      # dimensions text-embedding-ada-002


# ── Création de l'index ────────────────────────────────────────────────────
def ensure_index() -> dict:
    """Crée l'index Azure AI Search s'il n'existe pas encore."""
    try:
        _index_client.get_index(settings.azure_search_index)
        return {"status": "exists", "index": settings.azure_search_index}
    except HttpResponseError:
        pass  # index absent → on le crée

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="chunk_index", type=SearchFieldDataType.Int32),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMS,
            vector_search_profile_name="hnsw-profile"
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw")]
    )

    index = SearchIndex(
        name=settings.azure_search_index,
        fields=fields,
        vector_search=vector_search
    )

    _index_client.create_index(index)
    return {"status": "created", "index": settings.azure_search_index}


# ── Extraction de texte ────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrait le texte brut d'un PDF."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages_text.append(t.strip())
    return "\n\n".join(pages_text)


# ── Chunking ───────────────────────────────────────────────────────────────
def chunk_text(text: str, source: str) -> list[dict]:
    """Découpe le texte en chunks avec chevauchement."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        # Nettoyage basique
        chunk_text = re.sub(r'\s+', ' ', chunk_text).strip()

        if len(chunk_text) > 50:  # ignorer les chunks trop courts
            chunks.append({
                "id": str(uuid.uuid4()),
                "content": chunk_text,
                "source": source,
                "chunk_index": len(chunks)
            })

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# ── Pipeline d'ingestion ───────────────────────────────────────────────────
async def ingest_pdf(pdf_bytes: bytes, filename: str) -> dict:
    """
    Pipeline complet : PDF → texte → chunks → embeddings → index.
    Retourne un résumé de l'ingestion.
    """
    # 1. S'assurer que l'index existe
    ensure_index()

    # 2. Extraction du texte
    text = extract_text_from_pdf(pdf_bytes)
    if not text.strip():
        return {"error": "Impossible d'extraire du texte de ce PDF (scanné sans OCR ?)"}

    # 3. Chunking
    chunks = chunk_text(text, source=filename)
    if not chunks:
        return {"error": "Texte trop court pour être indexé"}

    # 4. Embedding + indexation par batch
    documents = []
    failed = 0

    for chunk in chunks:
        try:
            vector = await embed(chunk["content"])
            documents.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "embedding": vector
            })
        except Exception:
            failed += 1
            continue

    if not documents:
        return {"error": "Échec de l'embedding sur tous les chunks"}

    # Upload par batch de 100
    batch_size = 100
    uploaded = 0
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        result = _search_client.upload_documents(documents=batch)
        uploaded += sum(1 for r in result if r.succeeded)

    return {
        "success": True,
        "filename": filename,
        "total_chunks": len(chunks),
        "indexed": uploaded,
        "failed_embeddings": failed,
        "text_length": len(text)
    }


# ── Requête RAG ────────────────────────────────────────────────────────────
async def query_rag(question: str, source_filter: Optional[str] = None) -> dict:
    """
    Recherche vectorielle + génération de réponse sourcée.
    Le modèle répond UNIQUEMENT à partir des chunks retrouvés.
    """
    # 1. Embed la question
    try:
        question_vector = await embed(question)
    except Exception as e:
        return {"error": f"Échec de l'embedding de la question : {str(e)}"}

    # 2. Recherche vectorielle dans l'index
    vector_query = VectorizedQuery(
        vector=question_vector,
        k_nearest_neighbors=TOP_K,
        fields="embedding"
    )

    filter_expr = f"source eq '{source_filter}'" if source_filter else None

    try:
        results = _search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            filter=filter_expr,
            select=["content", "source", "chunk_index"],
            top=TOP_K
        )
        chunks = [
            {
                "content": r["content"],
                "source": r["source"],
                "chunk_index": r["chunk_index"]
            }
            for r in results
        ]
    except HttpResponseError as e:
        return {"error": f"Erreur Azure Search : {e.error.code} - {e.error.message}"}

    if not chunks:
        return {
            "question": question,
            "answer": "Aucune donnée pertinente trouvée dans vos archives. Uploadez d'abord des documents.",
            "sources": []
        }

    # 3. Construction du contexte pour GPT-4o
    context = "\n\n---\n\n".join(
        f"[Source: {c['source']} | Chunk #{c['chunk_index']}]\n{c['content']}"
        for c in chunks
    )

    # 4. Génération de la réponse sourcée
    prompt = f"""Tu es un assistant pour journalistes sportifs.
Réponds à la question suivante EN T'APPUYANT UNIQUEMENT sur les extraits fournis.
Si l'information n'est pas dans les extraits, dis-le explicitement.
Ne génère pas de faits non présents dans le contexte.

Question : {question}"""

    answer = await generate(prompt=prompt, context=context)

    return {
        "question": question,
        "answer": answer,
        "sources_used": [
            {"file": c["source"], "chunk": c["chunk_index"]}
            for c in chunks
        ],
        "nb_chunks_retrieved": len(chunks)
    }


# ── Comparaison de documents ───────────────────────────────────────────────
async def compare_documents(source1: str, source2: str, aspect: str = "") -> dict:
    """
    Compare deux documents indexés sur un aspect donné.
    Ex : comparer les performances d'un joueur dans deux matchs.
    """
    q = aspect if aspect else f"Comparaison entre {source1} et {source2}"

    # Requête sur chaque source séparément
    r1 = await query_rag(q, source_filter=source1)
    r2 = await query_rag(q, source_filter=source2)

    if "error" in r1 or "error" in r2:
        return {"error": "Impossible de récupérer les données pour la comparaison"}

    prompt = f"""Compare les deux extraits suivants sur le sujet : "{q}"

Document 1 ({source1}) :
{r1.get('answer', 'Aucune donnée')}

Document 2 ({source2}) :
{r2.get('answer', 'Aucune donnée')}

Fournis une analyse comparative structurée avec :
- Points communs
- Différences clés
- Conclusion journalistique"""

    comparison = await generate(prompt=prompt)

    return {
        "aspect": q,
        "document_1": source1,
        "document_2": source2,
        "comparison": comparison,
        "sources": {
            source1: r1.get("sources_used", []),
            source2: r2.get("sources_used", [])
        }
    }
