import os
import shutil
import uuid
from typing import Optional
from fastapi import FastAPI, Depends, File, Form, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas
from services.script_identifier import identify_script
from services.ocr_service import run_ocr
from services.restoration_service import restore_tamil_text
from services.modern_tamil_service import convert_to_modern_tamil
from services.translation_service import translate_to_english

# Automatically create/update database tables defined in models on application startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Maruthulir API",
    description="AI-based Tamil Heritage Restoration System backend for palm-leaf manuscripts and stone inscriptions.",
    version="2.0.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory path relative to project root
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount /uploads endpoint to serve manuscript images to the frontend
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/", summary="Welcome Endpoint")
def read_root():
    """
    Root GET endpoint returning welcome message and system status.
    """
    return {
        "message": "Welcome to Maruthulir - Tamil Heritage Restoration API",
        "status": "online",
        "docs_url": "/docs"
    }


@app.post(
    "/upload",
    response_model=schemas.ManuscriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Manuscript Image"
)
async def upload_manuscript(
    file: UploadFile = File(...),
    title: str = Form("Untitled Manuscript"),
    source_type: str = Form("palm-leaf"),
    script: str = Form("Tamil"),
    db: Session = Depends(get_db)
):
    """
    Upload an image file of a palm-leaf manuscript or stone inscription.
    Saves the image file to the uploads directory and stores manuscript metadata in PostgreSQL.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File provided is not a valid image."
        )

    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_save_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image file: {str(e)}"
        )

    relative_image_path = os.path.join("uploads", unique_filename)
    new_manuscript = models.Manuscript(
        title=title,
        source_type=source_type,
        script=script,
        image_path=relative_image_path,
        ocr_status="pending"
    )

    db.add(new_manuscript)
    db.commit()
    db.refresh(new_manuscript)

    return new_manuscript


@app.post(
    "/identify-script",
    response_model=schemas.ScriptIdentificationResponse,
    summary="Identify Manuscript Script"
)
async def api_identify_script(
    file: Optional[UploadFile] = File(None),
    manuscript_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyzes an uploaded manuscript image and identifies its script category:
    Tamil, Vatteluttu, Tamil-Brahmi, or Unknown.
    If manuscript_id is provided, updates the record in PostgreSQL.
    """
    image_bytes = None
    filename = None
    manuscript = None

    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")
        
        # Read image from disk
        full_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), manuscript.image_path)
        if os.path.exists(full_image_path):
            with open(full_image_path, "rb") as f:
                image_bytes = f.read()
            filename = manuscript.image_path

    if not image_bytes and file:
        image_bytes = await file.read()
        filename = file.filename

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Either file upload or valid manuscript_id must be provided.")

    # Perform script identification analysis
    result = identify_script(image_bytes, filename=filename)

    # Save to PostgreSQL database if manuscript record exists
    if manuscript:
        manuscript.detected_script = result["script"]
        manuscript.script_confidence = result["confidence"]
        manuscript.script_explanation = result["explanation"]
        db.commit()
        db.refresh(manuscript)

    return result


@app.post(
    "/ocr",
    response_model=schemas.OCRResponse,
    summary="Execute Tamil OCR on Manuscript"
)
async def api_ocr(
    file: Optional[UploadFile] = File(None),
    manuscript_id: Optional[int] = Form(None),
    script: Optional[str] = Form("Tamil"),
    db: Session = Depends(get_db)
):
    """
    Performs Document AI / Vision OCR on a manuscript image.
    Saves extracted text and confidence scores into the PostgreSQL database.
    """
    image_bytes = None
    manuscript = None

    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")

        full_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), manuscript.image_path)
        if os.path.exists(full_image_path):
            with open(full_image_path, "rb") as f:
                image_bytes = f.read()
        if manuscript.detected_script:
            script = manuscript.detected_script

    if not image_bytes and file:
        image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Either file upload or valid manuscript_id must be provided.")

    # Execute Sarvam Document AI OCR service
    ocr_result = run_ocr(image_bytes, script_name=script or "Tamil")

    # Update PostgreSQL database record
    if manuscript:
        manuscript.ocr_text = ocr_result["extracted_text"]
        manuscript.ocr_confidence = ocr_result["confidence"]
        manuscript.ocr_status = ocr_result["status"]
        db.commit()
        db.refresh(manuscript)

    return {
        "manuscript_id": manuscript_id,
        "extracted_text": ocr_result["extracted_text"],
        "confidence": ocr_result["confidence"],
        "status": ocr_result["status"],
        "message": ocr_result.get("message"),
        "provider": ocr_result.get("provider")
    }


@app.post(
    "/restore",
    response_model=schemas.RestorationResponse,
    summary="Restore Tamil Manuscript or Inscription Text"
)
async def api_restore(
    manuscript_id: Optional[int] = Form(None),
    text: Optional[str] = Form(None),
    source_type: Optional[str] = Form("palm-leaf"),
    db: Session = Depends(get_db)
):
    """
    Reads extracted OCR text for a manuscript or stone inscription, preserves original OCR text,
    generates restored/corrected Classical Tamil text grounded in Reference Lexicon,
    identifies source-specific damage evidence (palm-leaf vs stone erosion),
    and stores restoration results in PostgreSQL.
    """
    target_text = text
    manuscript = None
    st = source_type or "palm-leaf"

    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")
        if manuscript.source_type:
            st = manuscript.source_type
        if manuscript.ocr_status == "failed" or not manuscript.ocr_text:
            return {
                "manuscript_id": manuscript_id,
                "source_type": st,
                "original_ocr_text": "",
                "restored_text": "",
                "corrections": [],
                "damage_evidence": [],
                "confidence": None,
                "status": "failed",
                "message": "OCR unavailable - manuscript was not processed"
            }
        target_text = manuscript.ocr_text

    if not target_text:
        return {
            "manuscript_id": manuscript_id,
            "source_type": st,
            "original_ocr_text": "",
            "restored_text": "",
            "corrections": [],
            "damage_evidence": [],
            "confidence": None,
            "status": "failed",
            "message": "OCR unavailable - manuscript was not processed"
        }

    restoration_result = restore_tamil_text(target_text, source_type=st)

    if manuscript:
        # Preserve original ocr_text unchanged
        manuscript.restored_text = restoration_result["restored_text"]
        manuscript.restoration_confidence = restoration_result["confidence"]
        manuscript.restoration_status = restoration_result["status"]
        manuscript.corrections = restoration_result["corrections"]
        db.commit()
        db.refresh(manuscript)

    return {
        "manuscript_id": manuscript_id,
        "source_type": st,
        "original_ocr_text": target_text,
        "restored_text": restoration_result["restored_text"],
        "corrections": restoration_result["corrections"],
        "damage_evidence": restoration_result.get("damage_evidence", []),
        "confidence": restoration_result["confidence"],
        "status": restoration_result["status"],
        "message": restoration_result.get("message")
    }


@app.post(
    "/scholar-review",
    response_model=schemas.ScholarReviewResponse,
    summary="Scholar Review & Approval of Classical Tamil Text"
)
async def api_scholar_review(
    manuscript_id: Optional[int] = Form(None),
    approved_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Scholar inputs or approves the Classical Tamil text.
    Once approved, triggers generation of Modern Tamil paragraph and English translation,
    persisting the scholar-approved results in PostgreSQL.
    """
    manuscript = None
    st_display = "Palm-leaf Manuscript"
    
    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")
        st_display = "Stone Inscription" if ("stone" in manuscript.source_type.lower() or "inscription" in manuscript.source_type.lower()) else "Palm-leaf Manuscript"
        manuscript.restored_text = approved_text.strip()
        manuscript.restoration_status = "approved"

    # Generate student-friendly Modern Tamil paragraph
    modern_res = convert_to_modern_tamil(approved_text.strip())
    modern_text = modern_res.get("modern_tamil_text", "")
    
    # Generate English translation
    trans_res = translate_to_english(modern_text if (modern_res.get("status") == "completed" and modern_text) else approved_text.strip())
    english_text = trans_res.get("english_translation", "")

    if manuscript:
        manuscript.modern_tamil_text = modern_text
        manuscript.modern_tamil_status = modern_res.get("status", "completed")
        manuscript.english_translation = english_text
        manuscript.translation_status = trans_res.get("status", "completed")
        db.commit()
        db.refresh(manuscript)

    return {
        "manuscript_id": manuscript_id,
        "source_type": st_display,
        "approved_classical_tamil": approved_text.strip(),
        "modern_tamil_text": modern_text,
        "english_translation": english_text,
        "status": "completed",
        "message": "Scholar approval complete. Modern Tamil and English translation generated successfully."
    }


@app.post(
    "/convert-modern",
    response_model=schemas.ModernTamilResponse,
    summary="Convert Restored Tamil to Modern Tamil"
)
async def api_convert_modern(
    manuscript_id: Optional[int] = Form(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Reads restored Tamil text for a manuscript (or direct text input)
    and generates a readable Modern Tamil version (தற்கால எளிய உரை).
    Saves the modern Tamil text into PostgreSQL.
    """
    input_text = text
    manuscript = None

    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")
        if manuscript.ocr_status == "failed" or (not manuscript.restored_text and not manuscript.ocr_text):
            return {
                "manuscript_id": manuscript_id,
                "restored_text": "",
                "modern_tamil_text": "",
                "status": "failed",
                "message": "OCR unavailable - manuscript was not processed"
            }
        if manuscript.restored_text:
            input_text = manuscript.restored_text
        elif manuscript.ocr_text:
            input_text = manuscript.ocr_text

    if not input_text:
        return {
            "manuscript_id": manuscript_id,
            "restored_text": "",
            "modern_tamil_text": "",
            "status": "failed",
            "message": "OCR unavailable - manuscript was not processed"
        }

    modern_result = convert_to_modern_tamil(input_text)

    if manuscript:
        manuscript.modern_tamil_text = modern_result["modern_tamil_text"]
        manuscript.modern_tamil_status = modern_result["status"]
        db.commit()
        db.refresh(manuscript)

    return {
        "manuscript_id": manuscript_id,
        "restored_text": input_text,
        "modern_tamil_text": modern_result["modern_tamil_text"],
        "status": modern_result["status"],
        "message": modern_result.get("message")
    }


@app.post(
    "/translate-english",
    response_model=schemas.TranslationResponse,
    summary="Translate Modern Tamil to English"
)
@app.post(
    "/translate",
    response_model=schemas.TranslationResponse,
    summary="Translate Modern Tamil to English (Alias)"
)
async def api_translate_english(
    manuscript_id: Optional[int] = Form(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Reads Modern Tamil text for a manuscript (or direct text input)
    and generates an English translation.
    Saves the English translation into PostgreSQL.
    """
    input_text = text
    manuscript = None

    if manuscript_id:
        manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise HTTPException(status_code=404, detail="Manuscript record not found.")
        if manuscript.ocr_status == "failed" or (not manuscript.modern_tamil_text and not manuscript.restored_text and not manuscript.ocr_text):
            return {
                "manuscript_id": manuscript_id,
                "modern_tamil_text": "",
                "english_translation": "",
                "status": "failed",
                "message": "OCR unavailable - manuscript was not processed"
            }
        if manuscript.modern_tamil_text:
            input_text = manuscript.modern_tamil_text
        elif manuscript.restored_text:
            input_text = manuscript.restored_text
        elif manuscript.ocr_text:
            input_text = manuscript.ocr_text

    if not input_text:
        return {
            "manuscript_id": manuscript_id,
            "modern_tamil_text": "",
            "english_translation": "",
            "status": "failed",
            "message": "OCR unavailable - manuscript was not processed"
        }

    translation_result = translate_to_english(input_text)

    if manuscript:
        manuscript.english_translation = translation_result["english_translation"]
        manuscript.translation_status = translation_result["status"]
        db.commit()
        db.refresh(manuscript)

    return {
        "manuscript_id": manuscript_id,
        "modern_tamil_text": input_text,
        "english_translation": translation_result["english_translation"],
        "status": translation_result["status"],
        "message": translation_result.get("message"),
        "provider": translation_result.get("provider")
    }




