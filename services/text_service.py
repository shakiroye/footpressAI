from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from config import settings
import asyncio

client = TextAnalyticsClient(
    endpoint=settings.azure_ai_language_endpoint,
    credential=AzureKeyCredential(settings.azure_ai_language_key)
)

def _retry(fn, *args, retries=2, **kwargs):
    """Retry helper pour les appels Azure avec backoff."""
    for attempt in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except (ServiceRequestError, HttpResponseError) as e:
            if attempt == retries:
                raise
            import time; time.sleep(1.5 ** attempt)

async def summarize(text: str) -> dict:
    try:
        poller = _retry(client.begin_extract_summary, [text])
        results = poller.result()
        for result in results:
            if not result.is_error:
                sentences = [s.text for s in result.sentences]
                return {"summary": " ".join(sentences)}
        return {"error": "Résumé impossible"}
    except HttpResponseError as e:
        return {"error": f"Azure Language API error: {e.error.code} - {e.error.message}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}

async def extract_entities(text: str) -> dict:
    try:
        results = _retry(client.recognize_entities, [text])
        entities = [
            {
                "text": e.text,
                "category": e.category,
                "confidence": round(e.confidence_score, 2)
            }
            for doc in results if not doc.is_error
            for e in doc.entities
        ]
        return {"entities": entities}
    except HttpResponseError as e:
        return {"error": f"Azure Language API error: {e.error.code} - {e.error.message}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}

async def analyze_sentiment(text: str) -> dict:
    """Analyse le sentiment global et par phrase."""
    try:
        results = _retry(client.analyze_sentiment, [text], show_opinion_mining=True)
        for doc in results:
            if not doc.is_error:
                return {
                    "sentiment": doc.sentiment,
                    "scores": {
                        "positive": round(doc.confidence_scores.positive, 2),
                        "neutral": round(doc.confidence_scores.neutral, 2),
                        "negative": round(doc.confidence_scores.negative, 2)
                    },
                    "sentences": [
                        {
                            "text": s.text,
                            "sentiment": s.sentiment,
                            "opinions": [
                                {"target": o.target.text, "assessment": a.text, "sentiment": a.sentiment}
                                for o in (s.mined_opinions or [])
                                for a in o.assessments
                            ]
                        }
                        for s in doc.sentences
                    ]
                }
        return {"error": "Analyse de sentiment impossible"}
    except HttpResponseError as e:
        return {"error": f"Azure Language API error: {e.error.code} - {e.error.message}"}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}"}
