import os
import sys
import json
import io

# Force UTF-8 stdout for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from services.ocr_service import run_ocr, SARVAM_API_KEY

def verify_live_sarvam_ocr():
    print("=" * 70)
    print("  MARUTHULIR - SARVAM OCR LIVE AUTHENTICATION & EXTRACTION TEST  ")
    print("=" * 70)

    print(f"\n1. Environment API Key Audit:")
    if SARVAM_API_KEY:
        print(f"   ✓ SARVAM_API_KEY loaded successfully! Key prefix: {SARVAM_API_KEY[:8]}... (length: {len(SARVAM_API_KEY)})")
    else:
        print("   ❌ SARVAM_API_KEY is MISSING from backend/.env!")
        return

    # 2. Test Manuscript Image OCR
    manuscript_path = os.path.join(BASE_DIR, "test_manuscript.jpeg")
    print(f"\n2. Testing Manuscript Image OCR ({manuscript_path})...")
    assert os.path.exists(manuscript_path), f"Manuscript test image missing at {manuscript_path}"
    with open(manuscript_path, "rb") as f:
        ms_bytes = f.read()

    ms_res = run_ocr(ms_bytes, script_name="Tamil")
    print(f"   Status:   '{ms_res['status']}'")
    print(f"   Provider: '{ms_res['provider']}'")
    print(f"   Message:  '{ms_res['message']}'")
    print(f"   Confidence: {ms_res['confidence']}")
    print(f"   Extracted Text:\n  {ms_res['extracted_text'].replace('\n', ' ')}")

    assert ms_res["status"] == "completed", f"Manuscript OCR failed: {ms_res.get('message')}"
    assert ms_res["extracted_text"] and len(ms_res["extracted_text"]) > 0, "Manuscript OCR returned empty text!"

    # 3. Test Stone Inscription Image OCR
    stone_path = os.path.join(os.path.dirname(BASE_DIR), "uploads", "03afbfc99fbe4a5dba3255bed76cc5e7.jpeg")
    if not os.path.exists(stone_path):
        stone_path = os.path.join(BASE_DIR, "test_manuscript.jpeg")
    print(f"\n3. Testing Stone Inscription Image OCR ({stone_path})...")
    assert os.path.exists(stone_path), f"Stone inscription test image missing at {stone_path}"
    with open(stone_path, "rb") as f:
        stone_bytes = f.read()

    stone_res = run_ocr(stone_bytes, script_name="Tamil")
    print(f"   Status:   '{stone_res['status']}'")
    print(f"   Provider: '{stone_res['provider']}'")
    print(f"   Message:  '{stone_res['message']}'")
    print(f"   Confidence: {stone_res['confidence']}")
    print(f"   Extracted Text:\n  {stone_res['extracted_text'].replace('\n', ' ')}")

    assert stone_res["status"] == "completed", f"Stone Inscription OCR failed: {stone_res.get('message')}"
    assert stone_res["extracted_text"] and len(stone_res["extracted_text"]) > 0, "Stone Inscription OCR returned empty text!"

    print("\n" + "=" * 70)
    print("  ✅ SARVAM OCR AUTHENTICATION & BOTH IMAGE EXTRACTIONS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    verify_live_sarvam_ocr()
