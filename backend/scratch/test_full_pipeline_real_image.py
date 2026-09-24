import os
import sys
import io
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv('c:/Users/DELL/Downloads/maruthulir/backend/.env')

from services.ocr_service import run_ocr
from services.restoration_service import restore_tamil_text
from services.modern_tamil_service import convert_to_modern_tamil
from services.translation_service import translate_to_english

img_path = 'c:/Users/DELL/Downloads/maruthulir/uploads/manuscript test image.1.jpeg'
with open(img_path, 'rb') as f:
    img_bytes = f.read()

print("=" * 70)
print("  MARUTHULIR LIVE PIPELINE VERIFICATION ON REAL MANUSCRIPT  ")
print("=" * 70)

# Step 1: OCR
print("\n[STEP 1] Executing Real Sarvam Document AI OCR...")
ocr_res = run_ocr(img_bytes)
print(f"• Status:   {ocr_res['status']}")
print(f"• Provider: {ocr_res['provider']}")
print(f"• Raw OCR Text:\n{ocr_res['extracted_text']}\n")

assert ocr_res["status"] == "completed" and len(ocr_res["extracted_text"]) > 0

# Step 2: Restoration
print("[STEP 2] Executing Classical Tamil Text Restoration...")
restore_res = restore_tamil_text(ocr_res["extracted_text"])
print(f"• Status:      {restore_res['status']}")
print(f"• Confidence:  {restore_res['confidence']}")
print(f"• Corrections: {len(restore_res['corrections'])}")
print(f"• Restored Text:\n{restore_res['restored_text']}\n")

assert restore_res["status"] == "completed" and len(restore_res["restored_text"]) > 0

# Step 3: Modern Tamil Conversion
print("[STEP 3] Executing Modern Tamil Prose Conversion...")
modern_res = convert_to_modern_tamil(restore_res["restored_text"])
print(f"• Status:            {modern_res['status']}")
print(f"• Modern Tamil Text:\n{modern_res['modern_tamil_text']}\n")

assert modern_res["status"] == "completed" and len(modern_res["modern_tamil_text"]) > 0

# Step 4: English Translation
print("[STEP 4] Executing Sarvam AI English Translation...")
translate_res = translate_to_english(modern_res["modern_tamil_text"])
print(f"• Status:              {translate_res['status']}")
print(f"• Provider:            {translate_res['provider']}")
print(f"• English Translation:\n{translate_res['english_translation']}\n")

assert translate_res["status"] == "completed" and len(translate_res["english_translation"]) > 0

print("=" * 70)
print("  ✅ SUCCESS! REAL MANUSCRIPT PIPELINE PASSED 100% END-TO-END!  ")
print("=" * 70)
