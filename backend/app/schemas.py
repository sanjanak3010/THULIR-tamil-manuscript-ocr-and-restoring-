from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

class ManuscriptBase(BaseModel):
    title: str
    source_type: str  # e.g., 'palm-leaf', 'stone-inscription'
    script: str       # e.g., 'Tamil', 'Vatteluttu', 'Tamil-Brahmi'

class ManuscriptCreate(ManuscriptBase):
    """Schema for manuscript creation input metadata."""
    pass

class ManuscriptResponse(ManuscriptBase):
    """Schema for manuscript API JSON responses."""
    id: int
    image_path: str
    detected_script: Optional[str] = None
    script_confidence: Optional[float] = None
    script_explanation: Optional[str] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_status: Optional[str] = "pending"
    restored_text: Optional[str] = None
    restoration_confidence: Optional[float] = None
    restoration_status: Optional[str] = "pending"
    corrections: Optional[list] = None
    modern_tamil_text: Optional[str] = None
    modern_tamil_status: Optional[str] = "pending"
    english_translation: Optional[str] = None
    translation_status: Optional[str] = "pending"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ScriptIdentificationResponse(BaseModel):
    """Schema for POST /identify-script response."""
    script: str           # 'Tamil', 'Vatteluttu', 'Tamil-Brahmi', 'Unknown'
    confidence: Optional[float] = None     # Confidence score between 0.0 and 1.0 or None
    explanation: str      # Visual feature analysis explanation
    status: str           # 'success' or 'prototype_classified' or 'failed'

class OCRResponse(BaseModel):
    """Schema for POST /ocr response."""
    manuscript_id: Optional[int] = None
    extracted_text: str
    confidence: Optional[float] = None
    status: str           # 'completed' or 'failed'
    message: Optional[str] = None
    provider: Optional[str] = None

class RestorationResponse(BaseModel):
    """Schema for POST /restore response."""
    manuscript_id: Optional[int] = None
    source_type: Optional[str] = "palm-leaf"
    original_ocr_text: str
    restored_text: str
    corrections: list
    damage_evidence: Optional[list] = None
    confidence: Optional[float] = None
    status: str           # 'completed' or 'failed'
    message: Optional[str] = None

class ScholarReviewRequest(BaseModel):
    manuscript_id: Optional[int] = None
    approved_text: str

class ScholarReviewResponse(BaseModel):
    manuscript_id: Optional[int] = None
    source_type: str
    approved_classical_tamil: str
    modern_tamil_text: str
    english_translation: str
    status: str
    message: Optional[str] = None

class ModernTamilResponse(BaseModel):
    """Schema for POST /convert-modern response."""
    manuscript_id: Optional[int] = None
    restored_text: str
    modern_tamil_text: str
    status: str           # 'completed' or 'failed'
    message: Optional[str] = None

class TranslationResponse(BaseModel):
    """Schema for POST /translate response."""
    manuscript_id: Optional[int] = None
    modern_tamil_text: str
    english_translation: str
    status: str           # 'completed' or 'failed'
    message: Optional[str] = None
    provider: Optional[str] = None
