from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from config import settings

client = ImageAnalysisClient(
    endpoint=settings.azure_ai_vision_endpoint,
    credential=AzureKeyCredential(settings.azure_ai_vision_key)
)

async def analyze_image(image_bytes: bytes) -> dict:
    try:
        result = client.analyze(
            image_data=image_bytes,
            visual_features=[
                VisualFeatures.READ,
                VisualFeatures.TAGS
            ]
        )
        return {
            "text_extracted": [
                line.text
                for block in (result.read.blocks if result.read else [])
                for line in block.lines
            ],
            "tags": [t.name for t in (result.tags.list if result.tags else [])]
        }
    except Exception as e:
        return {"error": str(e)}
