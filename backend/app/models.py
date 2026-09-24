from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.database import Base

class Manuscript(Base):
    """
    SQLAlchemy Model representing a palm-leaf manuscript or stone inscription record.
    """
    __tablename__ = "manuscripts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # e.g., 'palm-leaf', 'stone-inscription'
    script = Column(String, nullable=False)       # User-selected or default script name
    image_path = Column(String, nullable=False)   # Relative/absolute path to stored uploaded image file
    
    # Day 2 Additions: Script Identification & OCR Results
    detected_script = Column(String, nullable=True)
    script_confidence = Column(Float, nullable=True)
    script_explanation = Column(String, nullable=True)
    
    ocr_text = Column(String, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    ocr_status = Column(String, nullable=True, default="pending")  # 'pending', 'completed', 'failed'
    
    # Day 3 Additions: Tamil Manuscript Restoration Layer
    restored_text = Column(String, nullable=True)
    restoration_confidence = Column(Float, nullable=True)
    restoration_status = Column(String, nullable=True, default="pending")
    corrections = Column(JSON, nullable=True)

    # Day 4 Step 3 Addition: Modern Tamil Conversion Layer
    modern_tamil_text = Column(String, nullable=True)
    modern_tamil_status = Column(String, nullable=True, default="pending")

    # Day 4 Step 4 Addition: English Translation Layer
    english_translation = Column(String, nullable=True)
    translation_status = Column(String, nullable=True, default="pending")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
