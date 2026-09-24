import os
import io
import json
import gzip
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# Sarvam AI API Key from environment
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip("'\" \t\r\n")

def _read_json_response(response) -> dict:
    """Helper to safely read and decompress response JSON from urllib response."""
    raw = response.read()
    if response.headers.get("Content-Encoding") == "gzip" or (len(raw) > 2 and raw[0] == 0x1f and raw[1] == 0x8b):
        try:
            raw = gzip.decompress(raw)
        except Exception as err:
            print(f"[Decompress warning] {err}")
    return json.loads(raw.decode("utf-8"))

def _extract_text_from_sarvam_res(res_data: dict) -> str:
    """Helper to extract OCR text from Sarvam Document AI response structure."""
    if not res_data:
        return ""
    if res_data.get("text"):
        return res_data["text"].strip()
    if res_data.get("transcript"):
        return res_data["transcript"].strip()

    texts = []
    for doc in res_data.get("documents", []):
        for page in doc.get("pages", []):
            for block in page.get("blocks", []):
                blk_txt = block.get("text", "").strip()
                if blk_txt:
                    texts.append(blk_txt)

    return "\n".join(texts).strip()

def run_ocr(image_bytes: bytes, script_name: str = "Tamil") -> Dict[str, Any]:
    """
    Executes Document AI / Vision OCR on an uploaded manuscript image using Sarvam AI API.
    Preserves raw OCR output text separately from downstream restoration.
    Strictly zero fake fallback: Returns failure status if API key is missing or request fails.

    Returns dictionary containing:
        - extracted_text (str): Raw OCR output text
        - confidence (Optional[float]): Numeric confidence score if provided by API, else None
        - status (str): 'completed' or 'failed'
        - message (str): Detail/status message
        - provider (str): Provider identifier
    """
    if not image_bytes:
        return {
            "extracted_text": "",
            "confidence": None,
            "status": "failed",
            "message": "No image data provided for OCR.",
            "provider": "Sarvam AI Document AI"
        }

    # If Sarvam API key is configured, call Sarvam API
    if SARVAM_API_KEY:
        # 1. Try Sarvam Document AI v1 Job Digitise API (POST /doc-ai/v1/job/digitise)
        try:
            url = "https://api.sarvam.ai/doc-ai/v1/job/digitise"
            boundary = "----WebKitFormBoundarySarvamDocAI7MA"
            body = []

            body.append(f"--{boundary}".encode())
            body.append(b'Content-Disposition: form-data; name="file"; filename="manuscript.jpg"')
            body.append(b'Content-Type: image/jpeg')
            body.append(b'')
            body.append(image_bytes)

            body.append(f"--{boundary}".encode())
            body.append(b'Content-Disposition: form-data; name="language_code"')
            body.append(b'')
            body.append(b'ta-IN')

            body.append(f"--{boundary}--".encode())
            body.append(b'')

            payload = b"\r\n".join(body)

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Accept-Encoding": "identity"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = _read_json_response(response)
                
                # Check if asynchronous job_id returned
                job_id = res_data.get("job_id")
                if job_id:
                    status_url = f"https://api.sarvam.ai/doc-ai/v1/job/{job_id}/status"
                    status_req = urllib.request.Request(
                        status_url,
                        headers={
                            "api-subscription-key": SARVAM_API_KEY,
                            "Accept-Encoding": "identity"
                        },
                        method="GET"
                    )
                    
                    for _ in range(12): # Poll up to 12 seconds
                        time.sleep(1)
                        with urllib.request.urlopen(status_req, timeout=10) as status_resp:
                            st_data = _read_json_response(status_resp)
                            job_status = st_data.get("status")
                            if job_status in ["completed", "partially_completed"]:
                                results_url = f"https://api.sarvam.ai/doc-ai/v1/job/{job_id}/results"
                                results_req = urllib.request.Request(
                                    results_url,
                                    headers={
                                        "api-subscription-key": SARVAM_API_KEY,
                                        "Accept-Encoding": "identity"
                                    },
                                    method="GET"
                                )
                                with urllib.request.urlopen(results_req, timeout=10) as res_resp:
                                    final_data = _read_json_response(res_resp)
                                    text = _extract_text_from_sarvam_res(final_data)
                                    conf = final_data.get("confidence")
                                    return {
                                        "extracted_text": text,
                                        "confidence": float(conf) if conf is not None else None,
                                        "status": "completed" if text else "failed",
                                        "message": "OCR completed via Sarvam Document AI (v1)" if text else "OCR unavailable - manuscript was not processed",
                                        "provider": "Sarvam AI Document AI (v1)"
                                    }
                            elif job_status in ["failed", "rejected"]:
                                break

                # Synchronous / Direct response handling
                text = _extract_text_from_sarvam_res(res_data)
                conf = res_data.get("confidence")
                if text:
                    return {
                        "extracted_text": text,
                        "confidence": float(conf) if conf is not None else None,
                        "status": "completed",
                        "message": "OCR completed via Sarvam Document AI",
                        "provider": "Sarvam AI Document AI"
                    }

        except Exception as err:
            print(f"[Sarvam Doc-AI v1 Warning] Endpoint error: {err}")

        # 2. Direct Vision API Endpoint (POST https://api.sarvam.ai/ocr)
        try:
            url = "https://api.sarvam.ai/ocr"
            boundary = "----WebKitFormBoundarySarvamOCR7MA4YW"
            body = [
                f"--{boundary}".encode(),
                b'Content-Disposition: form-data; name="file"; filename="manuscript.jpg"',
                b'Content-Type: image/jpeg',
                b'',
                image_bytes,
                f"--{boundary}".encode(),
                b'Content-Disposition: form-data; name="language_code"',
                b'',
                b'ta-IN',
                f"--{boundary}--".encode(),
                b''
            ]
            payload = b"\r\n".join(body)

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Accept-Encoding": "identity"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = _read_json_response(response)
                text = _extract_text_from_sarvam_res(res_data)
                conf = res_data.get("confidence")
                if text:
                    return {
                        "extracted_text": text,
                        "confidence": float(conf) if conf is not None else None,
                        "status": "completed",
                        "message": "OCR completed via Sarvam Vision API",
                        "provider": "Sarvam AI Vision OCR"
                    }
        except Exception as err:
            print(f"[Sarvam Vision Warning] Endpoint error: {err}")

    # ZERO FALLBACK: Return failure status if SARVAM_API_KEY is missing or API calls failed
    return {
        "extracted_text": "",
        "confidence": None,
        "status": "failed",
        "message": "OCR unavailable - manuscript was not processed",
        "provider": "Sarvam AI Document AI"
    }
