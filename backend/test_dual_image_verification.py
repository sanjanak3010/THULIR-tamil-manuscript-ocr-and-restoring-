"""
Dual-Image Verification and Zero-Fallback Security Test Script for Maruthulir backend.
Verifies that:
1. When SARVAM_API_KEY is missing/unreachable, OCR returns "OCR unavailable - manuscript was not processed" and empty text.
2. Downstream stages (Restoration, Modern Tamil, English Translation) are BLOCKED when OCR fails.
3. Absolutely NO hardcoded Tirukkural sample text ("அகர முதல", "ஆதி பகவன்") is returned for any image.
4. Image A and Image B process independently and produce separate outputs when sent to an active OCR service.
"""

import os
import sys
import io
from PIL import Image
from fastapi.testclient import TestClient

# Force UTF-8 stdout for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

import app.main as main_module
from app.main import app
from app.database import SessionLocal
from app.models import Manuscript

client = TestClient(app)

def run_dual_image_verification():
    print("=" * 75)
    print("  MARUTHULIR - ZERO FALLBACK & DUAL-IMAGE VERIFICATION SUITE  ")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # TEST 1: ZERO FALLBACK & DOWNSTREAM BLOCKING (WITHOUT SARVAM_API_KEY)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing Failed OCR & Downstream Stage Blocking (Zero Fallback)...")
    
    # Create Image A
    img_a_path = os.path.join(os.path.dirname(__file__), "manuscript_image_A.png")
    img_a = Image.new('RGB', (500, 120), color=(240, 220, 190))
    img_a.save(img_a_path, format="PNG")

    with open(img_a_path, "rb") as f:
        up_a = client.post(
            "/upload",
            data={"title": "Manuscript Image A (Test Strip 1)", "source_type": "palm-leaf", "script": "Tamil"},
            files={"file": ("manuscript_image_A.png", f, "image/png")}
        )
    assert up_a.status_code == 201
    id_a = up_a.json()["id"]
    print(f"✓ Uploaded Image A -> Assigned Manuscript ID: {id_a}")

    # Run OCR on Image A
    ocr_a = client.post("/ocr", data={"manuscript_id": id_a})
    assert ocr_a.status_code == 200
    res_a = ocr_a.json()
    
    print("\n  [Actual OCR Response for Image A (Unset API Key)]:")
    print(f"  • status:         '{res_a.get('status')}'")
    print(f"  • extracted_text: '{res_a.get('extracted_text')}'")
    print(f"  • confidence:     {res_a.get('confidence')}")
    print(f"  • message:        '{res_a.get('message')}'")
    print(f"  • provider:       '{res_a.get('provider')}'")

    # Assert ZERO fallback behavior
    assert res_a["status"] == "failed", "OCR status must be 'failed' when API key is missing!"
    assert res_a["extracted_text"] == "", "extracted_text must be empty when OCR fails!"
    assert res_a["confidence"] is None, "confidence must be None (Not provided) when OCR fails!"
    assert res_a["message"] == "OCR unavailable - manuscript was not processed"
    assert "அகர முதல" not in res_a["extracted_text"], "CRITICAL: Hardcoded Tirukkural text detected in OCR output!"
    print("✓ Zero-fallback assertion PASSED: No hardcoded Tirukkural text was returned.")

    # Test Downstream Blocking for Image A
    print("\n  [Testing Downstream Blocking on Failed OCR]:")
    
    rest_a = client.post("/restore", data={"manuscript_id": id_a}).json()
    print(f"  • /restore status:         '{rest_a.get('status')}', message: '{rest_a.get('message')}'")
    assert rest_a["status"] == "failed" and rest_a["restored_text"] == ""

    mod_a = client.post("/convert-modern", data={"manuscript_id": id_a}).json()
    print(f"  • /convert-modern status:  '{mod_a.get('status')}', message: '{mod_a.get('message')}'")
    assert mod_a["status"] == "failed" and mod_a["modern_tamil_text"] == ""

    trans_a = client.post("/translate-english", data={"manuscript_id": id_a}).json()
    print(f"  • /translate-english status: '{trans_a.get('status')}', message: '{trans_a.get('message')}'")
    assert trans_a["status"] == "failed" and trans_a["english_translation"] == ""

    print("✓ Downstream blocking assertion PASSED: Restoration, Modern Tamil, & English Translation blocked.")

    # -------------------------------------------------------------------------
    # TEST 2: DUAL-IMAGE PROCESSING WITH TWO DISTINCT MANUSCRIPT IMAGES
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing Dual-Image Processing with Two Distinct Manuscript Images...")

    # Create Image B (Substantially different image format and dimensions)
    img_b_path = os.path.join(os.path.dirname(__file__), "manuscript_image_B.png")
    img_b = Image.new('RGB', (250, 400), color=(180, 160, 130)) # Vertical inscription layout
    img_b.save(img_b_path, format="PNG")

    with open(img_b_path, "rb") as f:
        up_b = client.post(
            "/upload",
            data={"title": "Manuscript Image B (Stone Inscription Strip)", "source_type": "stone-inscription", "script": "Tamil-Brahmi"},
            files={"file": ("manuscript_image_B.png", f, "image/png")}
        )
    assert up_b.status_code == 201
    id_b = up_b.json()["id"]
    print(f"✓ Uploaded Image B -> Assigned Manuscript ID: {id_b}")

    original_run_ocr = main_module.run_ocr

    # Active Vision OCR mock for image comparison test
    def mock_active_sarvam_ocr(image_bytes: bytes, script_name: str = "Tamil") -> dict:
        # Inspect raw bytes of image to simulate distinct vision OCR response
        image = Image.open(io.BytesIO(image_bytes))
        w, h = image.size
        if w > h:
            # Palm-leaf horizontal strip
            text = "தமிழ் சுவடி - பனையோலை தொடர் 01"
            conf = 0.91
        else:
            # Stone inscription vertical format
            text = "கல்வெட்டு சாசனம் - தொன்மையான கல்வெட்டு எழுத்துக்கள் 02"
            conf = 0.85
        return {
            "extracted_text": text,
            "confidence": conf,
            "status": "completed",
            "message": "OCR completed via Sarvam AI Document AI",
            "provider": "Sarvam AI Document AI"
        }

    main_module.run_ocr = mock_active_sarvam_ocr

    try:
        # Run OCR for Image A
        ocr_resp_a = client.post("/ocr", data={"manuscript_id": id_a}).json()
        print("\n  [Actual OCR Response for Image A (Palm-Leaf Strip)]:")
        print(f"  • Manuscript ID:  {ocr_resp_a['manuscript_id']}")
        print(f"  • Extracted Text: '{ocr_resp_a['extracted_text']}'")
        conf_a_str = f"{ocr_resp_a['confidence'] * 100}%" if ocr_resp_a['confidence'] is not None else "Not provided"
        print(f"  • Confidence:     {conf_a_str}")
        print(f"  • Status:         '{ocr_resp_a['status']}'")

        # Run OCR for Image B
        ocr_resp_b = client.post("/ocr", data={"manuscript_id": id_b}).json()
        print("\n  [Actual OCR Response for Image B (Stone Inscription Strip)]:")
        print(f"  • Manuscript ID:  {ocr_resp_b['manuscript_id']}")
        print(f"  • Extracted Text: '{ocr_resp_b['extracted_text']}'")
        conf_b_str = f"{ocr_resp_b['confidence'] * 100}%" if ocr_resp_b['confidence'] is not None else "Not provided"
        print(f"  • Confidence:     {conf_b_str}")
        print(f"  • Status:         '{ocr_resp_b['status']}'")

        # Dual Image Assertions
        assert ocr_resp_a["extracted_text"] != ocr_resp_b["extracted_text"], "Image A and Image B must produce distinct OCR outputs!"
        assert "அகர முதல" not in ocr_resp_a["extracted_text"], "Image A must not contain hardcoded Tirukkural demo text!"
        assert "அகர முதல" not in ocr_resp_b["extracted_text"], "Image B must not contain hardcoded Tirukkural demo text!"
        
        print("\n✓ Dual-image distinction assertion PASSED: Image A and Image B produced distinct, non-sample outputs!")

    finally:
        main_module.run_ocr = original_run_ocr

    # Clean up test files
    for path in [img_a_path, img_b_path]:
        if os.path.exists(path):
            os.remove(path)

    print("\n" + "=" * 75)
    print("  ✅ ALL DUAL-IMAGE & ZERO-FALLBACK SECURITY TESTS PASSED SUCCESSFULLY!  ")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_dual_image_verification()
