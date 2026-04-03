"""
Middleware de monitoring — Option Bonus
----------------------------------------
- Log structuré de chaque requête (méthode, path, durée, statut)
- Compteurs en mémoire (requests, erreurs, temps moyen)
- Exposé via GET /metrics
"""

import time
import logging
from collections import defaultdict
from fastapi import Request

# ── Logger structuré ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("footpress")

# ── Métriques en mémoire ───────────────────────────────────────────────────
_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "total_duration_ms": 0.0,
    "requests_by_path": defaultdict(int),
    "errors_by_path": defaultdict(int),
    "requests_by_user": defaultdict(int),
}


async def monitoring_middleware(request: Request, call_next):
    """Middleware FastAPI : log + métriques sur chaque requête."""
    start = time.time()

    user_id = request.headers.get("X-User-ID", "anonymous")
    correlation_id = request.headers.get("X-Correlation-ID", "-")

    response = await call_next(request)

    duration_ms = round((time.time() - start) * 1000, 2)
    path = request.url.path

    # Mise à jour des métriques
    _metrics["total_requests"] += 1
    _metrics["total_duration_ms"] += duration_ms
    _metrics["requests_by_path"][path] += 1
    _metrics["requests_by_user"][user_id] += 1

    if response.status_code >= 400:
        _metrics["total_errors"] += 1
        _metrics["errors_by_path"][path] += 1

    # Log structuré
    logger.info(
        f"method={request.method} path={path} "
        f"status={response.status_code} duration={duration_ms}ms "
        f"user={user_id} correlation={correlation_id}"
    )

    # Ajout du correlation ID dans la réponse
    response.headers["X-Duration-Ms"] = str(duration_ms)
    response.headers["X-Correlation-ID"] = correlation_id

    return response


def get_metrics() -> dict:
    """Retourne les métriques actuelles."""
    total = _metrics["total_requests"]
    avg_duration = (
        round(_metrics["total_duration_ms"] / total, 2) if total > 0 else 0
    )
    error_rate = round(_metrics["total_errors"] / total * 100, 1) if total > 0 else 0

    return {
        "total_requests": total,
        "total_errors": _metrics["total_errors"],
        "error_rate_pct": error_rate,
        "avg_duration_ms": avg_duration,
        "requests_by_endpoint": dict(_metrics["requests_by_path"]),
        "errors_by_endpoint": dict(_metrics["errors_by_path"]),
        "active_users": len(_metrics["requests_by_user"]),
        "requests_by_user": dict(_metrics["requests_by_user"]),
    }
