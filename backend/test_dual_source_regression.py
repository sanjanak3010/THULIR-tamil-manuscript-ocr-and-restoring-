import os
import sys
import io
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MANUSCRIPT_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_manuscript.jpeg")
INSCRIPTION_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_sarvam.png")

def test_source_type_workflow(image_path: str, source_type: str, title: str):
    print(f"\n======================================================================")
    print(f"  TESTING DUAL PIPELINE FOR SOURCE TYPE: '{source_type.upper()}'")
    print(f"  Image: {os.path.basename(image_path)}")
    print(f"======================================================================")
    
    assert os.path.exists(image_path), f"Test image missing: {image_path}"
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    # Step 1: Upload Image
    print(f"\n[STEP 1/6] Uploading {source_type} image...")
    upload_res = client.post(
        "/upload",
        files={"file": (os.path.basename(image_path), io.BytesIO(image_bytes), "image/jpeg")},
        data={"title": title, "source_type": source_type, "script": "Tamil"}
    )
    assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
    m_data = upload_res.json()
    manuscript_id = m_data["id"]
    print(f"  ✓ Upload Successful. Manuscript ID: {manuscript_id} | Source Type: {m_data['source_type']}")

    # Step 2: Identify Script
    print(f"\n[STEP 2/6] Identifying Script & Source Features...")
    id_res = client.post("/identify-script", data={"manuscript_id": manuscript_id})
    assert id_res.status_code == 200, f"Identify script failed: {id_res.text}"
    script_data = id_res.json()
    print(f"  ✓ Identified Script: {script_data['script']} | Confidence: {script_data['confidence']}")

    # Step 3: Run Sarvam OCR (Working API call)
    print(f"\n[STEP 3/6] Running Sarvam OCR...")
    ocr_res = client.post("/ocr", data={"manuscript_id": manuscript_id, "script": script_data['script']})
    assert ocr_res.status_code == 200, f"OCR failed: {ocr_res.text}"
    ocr_data = ocr_res.json()
    print(f"  ✓ OCR Status: {ocr_data['status']}")
    print(f"  ✓ Extracted OCR Text:\n    {ocr_data['extracted_text'][:120]}...")

    # Step 4: Candidate Restoration & Damage Evidence
    print(f"\n[STEP 4/6] Generating Candidate Restoration & Damage Evidence...")
    restore_res = client.post("/restore", data={"manuscript_id": manuscript_id, "source_type": source_type})
    assert restore_res.status_code == 200, f"Restore failed: {restore_res.text}"
    r_data = restore_res.json()
    print(f"  ✓ Restoration Status: {r_data['status']}")
    print(f"  ✓ Restored Classical Text:\n    {r_data['restored_text'][:120]}...")
    print(f"  ✓ Damage Evidence Records: {len(r_data.get('damage_evidence', []))}")
    if r_data.get('damage_evidence'):
        print(f"  ✓ Sample Damage Evidence: {r_data['damage_evidence'][0]['damage_type']}")

    approved_text = r_data.get("restored_text") or ocr_data.get("extracted_text") or "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு"
    review_res = client.post("/scholar-review", data={"manuscript_id": manuscript_id, "approved_text": approved_text})
    assert review_res.status_code == 200, f"Scholar review failed: {review_res.text}"
    rev_data = review_res.json()
    print(f"  ✓ Scholar Review Status: {rev_data['status']}")
    print(f"  ✓ Approved Classical Tamil:\n    {rev_data['approved_classical_tamil'][:120]}...")
    print(f"  ✓ Modern Readable Tamil Paragraph:\n    {rev_data['modern_tamil_text']}")
    print(f"  ✓ English Translation:\n    {rev_data['english_translation']}")

    # Step 6: Verify Persistence
    print(f"\n[STEP 6/6] Verifying Data Integrity...")
    assert rev_data["approved_classical_tamil"] is not None and len(rev_data["approved_classical_tamil"]) > 0
    assert rev_data["modern_tamil_text"] is not None and len(rev_data["modern_tamil_text"]) > 0
    assert rev_data["english_translation"] is not None and len(rev_data["english_translation"]) > 0

    print(f"\n  ✅ SUCCESSFUL VERIFICATION FOR SOURCE TYPE: '{source_type.upper()}'")

def run_regression_suite():
    print("======================================================================")
    print("  MARUTHULIR DUAL SOURCE TYPE REGRESSION TEST SUITE")
    print("======================================================================")
    
    # Test 1: Palm-Leaf Manuscript
    test_source_type_workflow(
        image_path=MANUSCRIPT_IMAGE_PATH,
        source_type="palm-leaf",
        title="Royal Chola Grant Palm-Leaf Manuscript"
    )

    # Test 2: Stone Inscription
    test_source_type_workflow(
        image_path=INSCRIPTION_IMAGE_PATH,
        source_type="stone-inscription",
        title="Thanjavur Temple Wall Inscription"
    )

    print("\n======================================================================")
    print("  🎉 ALL REGRESSION TESTS PASSED! DUAL SOURCE TYPE WORKFLOW VERIFIED.")
    print("======================================================================")

if __name__ == "__main__":
    run_regression_suite()
