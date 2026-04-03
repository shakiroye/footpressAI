"""
Sécurité — API Key + isolation multi-utilisateurs
---------------------------------------------------
- Authentification via header X-API-Key
- Chaque utilisateur a son espace isolé dans le RAG (préfixe source)
- Clés définies dans .env (FOOTPRESS_API_KEYS)
"""

from fastapi import Header, HTTPException, status
from config import settings

_raw = settings.footpress_api_keys
VALID_API_KEYS: dict[str, str] = {}

for entry in _raw.split(","):
    entry = entry.strip()
    if entry:
        # Format : "user_id:api_key" ou juste "api_key" (user = anonymous)
        if ":" in entry:
            uid, key = entry.split(":", 1)
            VALID_API_KEYS[key.strip()] = uid.strip()
        else:
            VALID_API_KEYS[entry] = "anonymous"


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Dépendance FastAPI : vérifie la clé API et retourne l'user_id.
    Usage : user_id: str = Depends(require_api_key)
    """
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide. Ajoutez X-API-Key dans vos headers.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return VALID_API_KEYS[x_api_key]


async def optional_api_key(
    x_api_key: str = Header(None, alias="X-API-Key")
) -> str:
    """
    Dépendance optionnelle : retourne l'user_id ou 'anonymous'.
    Utilisée sur les endpoints non bloquants.
    """
    if x_api_key and x_api_key in VALID_API_KEYS:
        return VALID_API_KEYS[x_api_key]
    return "anonymous"
