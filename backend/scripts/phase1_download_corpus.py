import os
import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_RAW_DIR = os.path.join(os.path.dirname(PROJECT_ROOT), "corpus_raw")
os.makedirs(CORPUS_RAW_DIR, exist_ok=True)

ETEXT_FILES = [
    "pmuni0001.html",     # Thirukkural
    "pmuni0002.html",     # Athichudi, Kondrai Vendhan, Nalvazhi, Moodhurai
    "pmuni0003_01.html",  # Thiruvasagam 1
    "pmuni0003_02.html",  # Thiruvasagam 2
    "pmuni0004.html",     # Naladiyar
    "pmuni0014.html",     # Manimekalai
    "pmuni0017.html",     # Abhirami Anthathi
    "pmuni0036.html",     # Pazhamozhi 400
    "pmuni0048.html",     # Kamba Ramayanam
    "pmuni0050.html",     # Purananuru
    "pmuni0052.html",     # Akananuru
    "pmuni0053.html",     # Natrinai
    "pmuni0054.html",     # Kuruntokai
    "pmuni0055.html",     # Kalithokai
]

BASE_URL = "https://www.projectmadurai.org/pm_etexts/utf8/"

def download_and_check_encoding():
    results = []
    tscii_detected = False

    print("=== PHASE 1: CORPUS ACQUISITION ===")
    print(f"Target Directory: {CORPUS_RAW_DIR}")
    print(f"Downloading {len(ETEXT_FILES)} Classical Tamil etexts from Project Madurai...\n")

    for etext_filename in ETEXT_FILES:
        target_url = BASE_URL + etext_filename
        save_path = os.path.join(CORPUS_RAW_DIR, etext_filename)
        
        try:
            req = urllib.request.Request(
                target_url,
                headers={"User-Agent": "MaruthulirCorpusAcquisition/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_bytes = resp.read()

            # Verify UTF-8 decoding vs actual legacy TSCII content charset
            is_utf8 = True
            try:
                decoded_str = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                is_utf8 = False
                tscii_detected = True

            # Also check if meta header specifically specifies non-utf8 charset
            meta_tscii = b'charset="tscii"' in content_bytes.lower() or b"charset='tscii'" in content_bytes.lower()
            if meta_tscii or not is_utf8:
                tscii_detected = True
                print(f"  [WARNING] Legacy non-Unicode TSCII detected in {etext_filename}!")

            # Save raw file
            with open(save_path, "wb") as f:
                f.write(content_bytes)

            results.append({
                "filename": etext_filename,
                "url": target_url,
                "size_bytes": len(content_bytes),
                "encoding": "TSCII" if (meta_tscii or not is_utf8) else "UTF-8",
                "status": "success"
            })
            print(f"  ✓ Saved {etext_filename} ({len(content_bytes):,} bytes) - Encoding: UTF-8")

        except Exception as e:
            results.append({
                "filename": etext_filename,
                "url": target_url,
                "size_bytes": 0,
                "encoding": "unknown",
                "status": f"failed: {str(e)}"
            })
            print(f"  ✗ Failed {etext_filename}: {e}")

    report_path = os.path.join(CORPUS_RAW_DIR, "phase1_report.json")
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump({"results": results, "tscii_detected": tscii_detected}, rf, indent=2)

    print("\n=== PHASE 1 SUMMARY ===")
    print(f"Total Files Processed: {len(results)}")
    print(f"Successful Downloads: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"TSCII Encoding Detected: {tscii_detected}")
    print(f"Phase 1 Metadata Log: {report_path}")

    return results, tscii_detected

if __name__ == "__main__":
    download_and_check_encoding()
