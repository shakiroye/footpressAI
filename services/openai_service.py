from openai import AsyncAzureOpenAI, APITimeoutError, APIConnectionError, APIStatusError
from config import settings
import asyncio

client = AsyncAzureOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_key,
    api_version="2024-10-21"
)

async def generate(prompt: str, context: str = "") -> str:
    messages = [
        {
            "role": "system",
            "content": "Tu es un assistant pour journalistes sportifs. Sois précis, factuel et sourcé."
        }
    ]
    if context:
        messages.append({
            "role": "system",
            "content": f"Contexte disponible :\n{context}"
        })
    messages.append({"role": "user", "content": prompt})

    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
                timeout=30.0
            )
            return response.choices[0].message.content
        except APITimeoutError:
            if attempt == 2:
                return "Erreur : délai d'attente dépassé (timeout 30s). Réessayez."
            await asyncio.sleep(1.5 ** attempt)
        except APIConnectionError:
            if attempt == 2:
                return "Erreur : impossible de joindre Azure OpenAI. Vérifiez votre connexion."
            await asyncio.sleep(1.5 ** attempt)
        except APIStatusError as e:
            return f"Erreur Azure OpenAI [{e.status_code}]: {e.message}"
        except Exception as e:
            return f"Erreur inattendue OpenAI : {str(e)}"

async def embed(text: str) -> list[float]:
    """Génère un vecteur — utilisé par le pipeline RAG (défi 2)."""
    response = await client.embeddings.create(
        model=settings.azure_openai_emb_deployment,
        input=text
    )
    return response.data[0].embedding
