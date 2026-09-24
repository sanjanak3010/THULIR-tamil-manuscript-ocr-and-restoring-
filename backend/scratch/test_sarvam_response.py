import os
import io
import json
import gzip
import urllib.request
from PIL import Image
from dotenv import load_dotenv

load_dotenv('c:/Users/DELL/Downloads/maruthulir/backend/.env')
key = os.getenv('SARVAM_API_KEY')
print("API Key loaded, length:", len(key) if key else 0)

url = "https://api.sarvam.ai/doc-ai/v1/job/digitise"
boundary = "----WebKitFormBoundarySarvamDocAI7MA"
body = []

img = Image.new('RGB', (400, 100), color=(250, 240, 220))
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

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        raw = response.read()
        print("Response headers:", dict(response.headers))
        print("Raw starts with gzip magic header?:", raw.startswith(b'\x1f\x8b'))
        if response.headers.get("Content-Encoding") == "gzip" or raw.startswith(b'\x1f\x8b'):
            raw = gzip.decompress(raw)
        res_data = json.loads(raw.decode("utf-8"))
        print("SUCCESS! Parsed Response JSON:", res_data)
except Exception as e:
    import traceback
    traceback.print_exc()
