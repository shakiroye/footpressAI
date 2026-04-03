from fastapi import UploadFile
from typing import Optional

def detect_input_type(
    text: Optional[str],
    file: Optional[UploadFile]
) -> str:
    if file:
        content_type = file.content_type or ""
        if content_type.startswith("image/"):
            return "image"
        if "pdf" in content_type:
            if text:
                return "pdf_with_question"
            return "pdf_summary"

    if text:
        keywords = ["match", "joueur", "score", "but", "équipe", "club", "vs",
                    "goal", "assist", "classement", "saison", "derby"]
        if any(kw in text.lower() for kw in keywords):
            return "football_query"
        return "text"

    return "unknown"
