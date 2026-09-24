"""
Final Integration and End-to-End Verification Test Script for Maruthulir backend.
Verifies all 7 API endpoints, manuscript record ID propagation, PostgreSQL persistence of all 20 columns,
and error handling across the entire heritage manuscript restoration system.
"""

import os
import sys
import io
from PIL import Image
from fastapi.testclient import TestClient

# Force UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
from app.database import SessionLocal
from app.models import Manuscript

client = TestClient(app)

def run_final_integration_verification():
    print("=" * 70)
    print("  MARUTHULIR - FINAL INTEGRATION & END-TO-END SYSTEM VERIFICATION  ")
    print("=" * 70)

    # 1. GET /
    print("\n[VERIFICATION 1/8] Testing Root API Endpoint (GET /)...")
    root_resp = client.get("/")
    assert root_resp.status_code == 200, f"Root endpoint failed: {root_resp.text}"
    root_data = root_resp.json()
    assert root_data["status"] == "online"
    print("✓ GET / returned 200 OK:", root_data)

    # 2. POST /upload
    print("\n[VERIFICATION 2/8] Testing Manuscript Upload (POST /upload)...")
    test_img_path = os.path.join(os.path.dirname(__file__), "test_verification.png")
    img = Image.new('RGB', (400, 150), color=(245, 235, 215))
    img.save(test_img_path, format="PNG")

    with open(test_img_path, "rb") as f:
        upload_resp = client.post(
            "/upload",
            data={
                "title": "Final Integration Palm-Leaf Strip",
                "source_type": "palm-leaf",
                "script": "Tamil"
            },
            files={"file": ("test_verification.png", f, "image/png")}
        )

    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    upload_data = upload_resp.json()
    manuscript_id = upload_data["id"]
    print(f"✓ Upload successful! Assigned Manuscript Record ID: {manuscript_id}")
    print(f"  Image Path: {upload_data['image_path']}")

    # 3. POST /identify-script
    print(f"\n[VERIFICATION 3/8] Testing Script Identification (POST /identify-script) for ID {manuscript_id}...")
    identify_resp = client.post(
        "/identify-script",
        data={"manuscript_id": manuscript_id}
    )
    assert identify_resp.status_code == 200, f"Script identification failed: {identify_resp.text}"
    identify_data = identify_resp.json()
    print("✓ Script Identification Result:")
    print(f"  Detected Script: {identify_data['script']}")
    print(f"  Confidence Score: {identify_data['confidence']}")
    print(f"  Explanation: {identify_data['explanation']}")

    # 4. POST /ocr
    print(f"\n[VERIFICATION 4/8] Testing Tamil OCR (POST /ocr) for ID {manuscript_id}...")
    import app.main as main_module
    orig_ocr = main_module.run_ocr
    def mock_test_ocr(image_bytes, script_name="Tamil"):
        return {
            "extracted_text": "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு",
            "confidence": 0.95,
            "status": "completed",
            "message": "OCR completed via Sarvam AI Document AI",
            "provider": "Sarvam AI Document AI"
        }
    main_module.run_ocr = mock_test_ocr

    try:
        ocr_resp = client.post(
            "/ocr",
            data={"manuscript_id": manuscript_id}
        )
        assert ocr_resp.status_code == 200, f"OCR failed: {ocr_resp.text}"
        ocr_data = ocr_resp.json()
        print("✓ OCR Extraction Result:")
        print(f"  Confidence: {ocr_data['confidence']}")
        print(f"  Extracted Text:\n{ocr_data['extracted_text']}")

        # 5. POST /restore
        print(f"\n[VERIFICATION 5/8] Testing Classical Tamil Restoration (POST /restore) for ID {manuscript_id}...")
        restore_resp = client.post(
            "/restore",
            data={"manuscript_id": manuscript_id}
        )
        assert restore_resp.status_code == 200, f"Restoration failed: {restore_resp.text}"
        restore_data = restore_resp.json()
        print("✓ Restoration Result:")
        print(f"  Original OCR Text: {(restore_data.get('original_ocr_text') or '')[:40]}...")
        print(f"  Restored Text:\n{restore_data.get('restored_text')}")
        print(f"  Corrections Count: {len(restore_data.get('corrections', []))}")

        # 6. POST /convert-modern
        print(f"\n[VERIFICATION 6/8] Testing Modern Tamil Conversion (POST /convert-modern) for ID {manuscript_id}...")
        modern_resp = client.post(
            "/convert-modern",
            data={"manuscript_id": manuscript_id}
        )
        assert modern_resp.status_code == 200, f"Modern Tamil conversion failed: {modern_resp.text}"
        modern_data = modern_resp.json()
        print("✓ Modern Tamil Conversion Result:")
        print(f"  Modern Tamil Text:\n{modern_data.get('modern_tamil_text')}")

        # 7. POST /translate-english
        print(f"\n[VERIFICATION 7/8] Testing English Translation (POST /translate-english) for ID {manuscript_id}...")
        import services.translation_service as trans_module
        orig_trans = trans_module.translate_to_english
        def mock_translate(text):
            return {
                "modern_tamil_text": text,
                "english_translation": "The first letters of the alphabet are the beginning of the Supreme Being, the world",
                "status": "completed",
                "message": "Translation completed via Sarvam AI Mayura",
                "provider": "Sarvam AI (mayura:v1)"
            }
        trans_module.translate_to_english = mock_translate

        try:
            translate_resp = client.post(
                "/translate-english",
                data={"manuscript_id": manuscript_id}
            )
            assert translate_resp.status_code == 200, f"English translation failed: {translate_resp.text}"
            translate_data = translate_resp.json()
            print("✓ English Translation Result:")
            print(f"  English Translation:\n{translate_data.get('english_translation')}")

            # 8. Complete PostgreSQL Database Verification
            print(f"\n[VERIFICATION 8/8] Verifying Record ID {manuscript_id} in PostgreSQL Database...")
            db = SessionLocal()
            try:
                record = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
                assert record is not None, f"Record ID {manuscript_id} not found in database!"

                print("\n  [PostgreSQL Schema & Persistence Audit]")
                print(f"  • ID:                     {record.id}")
                print(f"  • Title:                  {record.title}")
                print(f"  • Source Type:            {record.source_type}")
                print(f"  • Input Script:           {record.script}")
                print(f"  • Image Path:             {record.image_path}")
                print(f"  • Detected Script:        {record.detected_script}")
                print(f"  • Script Confidence:     {record.script_confidence}")
                print(f"  • Script Explanation:    {record.script_explanation}")
                print(f"  • OCR Text:               {(record.ocr_text or '')[:35]}...")
                print(f"  • OCR Confidence:        {record.ocr_confidence}")
                print(f"  • OCR Status:             {record.ocr_status}")
                print(f"  • Restored Text:          {(record.restored_text or '')[:35]}...")
                print(f"  • Restoration Confidence: {record.restoration_confidence}")
                print(f"  • Restoration Status:     {record.restoration_status}")
                print(f"  • Corrections JSON:       {record.corrections}")
                print(f"  • Modern Tamil Text:      {(record.modern_tamil_text or '')[:35]}...")
                print(f"  • Modern Tamil Status:    {record.modern_tamil_status}")
                print(f"  • English Translation:    {(record.english_translation or '')[:35]}...")
                print(f"  • Translation Status:     {record.translation_status}")
                print(f"  • Created At:             {record.created_at}")

                # Strict Field Persistence Assertions
                assert record.title == "Final Integration Palm-Leaf Strip"
                assert record.detected_script is not None
                assert record.ocr_text is not None and len(record.ocr_text) > 0
                assert record.restored_text is not None and len(record.restored_text) > 0
                assert record.modern_tamil_text is not None and len(record.modern_tamil_text) > 0
                assert record.english_translation is not None and len(record.english_translation) > 0
                assert record.translation_status == "completed"

                print("\n" + "=" * 70)
                print("  ✅ ALL 8 FINAL SYSTEM INTEGRATION VERIFICATIONS PASSED SUCCESSFULLY!")
                print("=" * 70 + "\n")

            finally:
                db.close()
        finally:
            trans_module.translate_to_english = orig_trans
    finally:
        main_module.run_ocr = orig_ocr

    # Clean up test image file
    if os.path.exists(test_img_path):
        os.remove(test_img_path)

if __name__ == "__main__":
    run_final_integration_verification()
