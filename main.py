from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from routers import ai_router, rag_router, pipeline_router
from middleware.logging_middleware import monitoring_middleware, get_metrics

app = FastAPI(
    title="FootPress AI",
    description="Assistant intelligent pour journalistes sportifs",
    version="1.0.0"
)

# ── Middleware monitoring ──────────────────────────────────────────────────
app.add_middleware(BaseHTTPMiddleware, dispatch=monitoring_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router.router, prefix="/api/v1")
app.include_router(rag_router.router, prefix="/api/v1")
app.include_router(pipeline_router.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FootPress AI"}

@app.get("/metrics", tags=["Bonus - Monitoring"])
async def metrics():
    """
    [BONUS] Métriques en temps réel du système.
    - Nombre total de requêtes
    - Taux d'erreur
    - Durée moyenne de réponse
    - Requêtes par endpoint et par utilisateur
    """
    return get_metrics()

@app.get("/info")
async def info():
    """Justification des choix d'architecture et de services."""
    return {
        "use_case": "FootPress AI — assistant pour journalistes sportifs",
        "probleme_reel": (
            "Les journalistes sportifs traitent quotidiennement des dizaines de matchs, "
            "statistiques, interviews et documents. Ce backend automatise l'analyse, "
            "la structuration et l'enrichissement de ces contenus."
        ),
        "architecture": {
            "pattern": "Un seul endpoint intelligent (POST /api/v1/analyze/)",
            "justification": (
                "Évite le code spaghetti avec 15 endpoints spécialisés. "
                "Le router_service détecte automatiquement le type d'entrée "
                "(texte brut, query football, image, PDF) et orchestre les bons services."
            ),
            "separation_responsabilites": {
                "routers/": "Couche HTTP — reçoit, valide, retourne",
                "services/": "Couche métier — logique IA et appels Azure",
                "config.py": "Centralisation des paramètres via .env"
            }
        },
        "choix_services": {
            "Azure_OpenAI_gpt4o": "Génération de contenu journalistique structuré, enrichissement et analyse contextuelle",
            "Azure_AI_Language": "Résumé extractif, extraction d'entités nommées (joueurs, clubs, lieux) et analyse de sentiment avec opinion mining",
            "Azure_AI_Vision": "OCR sur captures de tableaux de stats, extraction de tags pour classifier les images de match",
            "Azure_Blob_Storage": "Stockage scalable des PDFs uploadés par les journalistes",
            "Azure_AI_Search": "Recherche vectorielle pour le pipeline RAG — retrouve les chunks pertinents dans les archives"
        },
        "couche_intelligence": (
            "Ce backend n'est pas une simple passerelle : il combine les résultats "
            "de plusieurs services (Language + OpenAI) pour produire une sortie "
            "enrichie et structurée. Le router adapte dynamiquement le pipeline "
            "selon l'entrée reçue."
        ),
        "limites_connues": {
            "hallucinations": "GPT-4o peut inventer des statistiques — toujours vérifier les faits générés",
            "quota_etudiant": "Capacité limitée à 1K tokens/min — pas adapté à une charge de production",
            "langue": "Les modèles Language performent mieux en anglais qu'en français",
            "vision_caption": "Azure Vision (Sweden Central) ne supporte pas la feature Caption"
        },
        "couts": {
            "Azure_AI_Language": "Free F0 — 5000 transactions/mois",
            "Azure_AI_Vision": "Free F0 — 5000 transactions/mois",
            "Azure_AI_Search": "Free — 1 index, 50MB",
            "Azure_OpenAI": "Standard S0 — facturation à l'usage (~0.005$/1K tokens)",
            "conseil": "En production, monitorer les tokens consommés et limiter max_tokens selon le use case"
        }
    }
