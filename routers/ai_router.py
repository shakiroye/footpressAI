from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from services.router_service import detect_input_type
from services import text_service, vision_service, openai_service

router = APIRouter(prefix="/analyze", tags=["Défi 1 - AI Playground"])

@router.post("/")
async def analyze(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Endpoint intelligent unique.
    Adapte automatiquement le traitement selon ce qu'il reçoit.
    """
    input_type = detect_input_type(text, file)

    if input_type == "image":
        image_bytes = await file.read()
        result = await vision_service.analyze_image(image_bytes)
        if result.get("text_extracted"):
            extracted = "\n".join(result["text_extracted"])
            result["analysis"] = await openai_service.generate(
                prompt="Analyse ces statistiques extraites d'une image de match.",
                context=extracted
            )
        return {"type": input_type, "result": result}

    if input_type == "text":
        summary = await text_service.summarize(text)
        entities = await text_service.extract_entities(text)
        sentiment = await text_service.analyze_sentiment(text)
        enriched = await openai_service.generate(
            prompt=f"Enrichis et structure ces notes de journaliste : {text}"
        )
        return {
            "type": input_type,
            "summary": summary,
            "entities": entities,
            "sentiment": sentiment,
            "enriched": enriched
        }

    if input_type == "football_query":
        response = await openai_service.generate(prompt=text)
        return {"type": input_type, "response": response}

    if input_type == "pdf_with_question":
        return {
            "type": input_type,
            "message": "Utilisez /api/v1/rag/query pour interroger vos archives PDF"
        }

    return {"type": "unknown", "message": "Entrée non reconnue"}
