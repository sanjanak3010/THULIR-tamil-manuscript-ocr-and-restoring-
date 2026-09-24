import os
import io
import json
import gzip
import time
import urllib.request
from PIL import Image
from dotenv import load_dotenv

load_dotenv('c:/Users/DELL/Downloads/maruthulir/backend/.env')
key = os.getenv('SARVAM_API_KEY')

url = "https://api.sarvam.ai/doc-ai/v1/job/digitise"
boundary = "----WebKitFormBoundarySarvamDocAI7MA"
body = []

img = Image.new('RGB', (500, 120), color=(250, 240, 220))
buf = io.BytesIO()
img.save(buf, format='JPEG')
image_bytes = buf.getvalue()

body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="file"; filename="manuscript.jpg"')
body.append(b'Content-Type: image/jpeg')
body.append(b'')
body.append(image_bytes)

body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="language"')
body.append(b'')
body.append(b'ta-IN')

body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="output_format"')
body.append(b'')
body.append(b'json')

body.append(f"--{boundary}--".encode())
body.append(b'')

payload = b"\r\n".join(body)

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "api-subscription-key": key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept-Encoding": "identity"
    },
    method="POST"
)

with urllib.request.urlopen(req, timeout=15) as response:
    raw = response.read()
    if response.headers.get("Content-Encoding") == "gzip" or raw.startswith(b'\x1f\x8b'):
        raw = gzip.decompress(raw)
    res_data = json.loads(raw.decode("utf-8"))
    job_id = res_data.get("job_id")
    print("Job ID:", job_id)

    status_url = f"https://api.sarvam.ai/doc-ai/v1/job/{job_id}/status"
    status_req = urllib.request.Request(
        status_url,
        headers={"api-subscription-key": key, "Accept-Encoding": "identity"},
        method="GET"
    )
    
    for i in range(15):
        time.sleep(1)
        with urllib.request.urlopen(status_req, timeout=10) as st_resp:
            st_raw = st_resp.read()
            if st_resp.headers.get("Content-Encoding") == "gzip" or st_raw.startswith(b'\x1f\x8b'):
                st_raw = gzip.decompress(st_raw)
            st_data = json.loads(st_raw.decode("utf-8"))
            print(f"Poll {i}: status =", st_data.get("status"))
            if st_data.get("status") in ["completed", "partially_completed"]:
                results_url = f"https://api.sarvam.ai/doc-ai/v1/job/{job_id}/results"
                results_req = urllib.request.Request(
                    results_url,
                    headers={"api-subscription-key": key, "Accept-Encoding": "identity"},
                    method="GET"
                )
                with urllib.request.urlopen(results_req, timeout=10) as res_resp:
                    res_raw = res_resp.read()
                    if res_resp.headers.get("Content-Encoding") == "gzip" or res_raw.startswith(b'\x1f\x8b'):
                        res_raw = gzip.decompress(res_raw)
                    final_data = json.loads(res_raw.decode("utf-8"))
                    print("FINAL RESULTS JSON STRUCTURE:")
                    print(json.dumps(final_data, indent=2, ensure_ascii=False))
                break
