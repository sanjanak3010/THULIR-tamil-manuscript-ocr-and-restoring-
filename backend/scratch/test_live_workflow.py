import os
import io
import json
from PIL import Image, ImageDraw, ImageFont
import urllib.request

# Create a sample Tamil manuscript image
img = Image.new('RGB', (600, 150), color=(245, 235, 215))
d = ImageDraw.Draw(img)
d.text((30, 40), "தமிழ்ச்சுவடி உரை வாழ்க தமிழ்மொழி", fill=(40, 20, 10))

img_buf = io.BytesIO()
img.save(img_buf, format="JPEG")
img_bytes = img_buf.getvalue()

boundary = "----WebKitFormBoundaryLiveWorkflowTest"
body = []
body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="file"; filename="real_manuscript.jpg"')
body.append(b'Content-Type: image/jpeg')
body.append(b'')
body.append(img_bytes)
body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="title"')
body.append(b'')
body.append(b'Live Browser Workflow Test')
body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="source_type"')
body.append(b'')
body.append(b'palm-leaf')
body.append(f"--{boundary}".encode())
body.append(b'Content-Disposition: form-data; name="script"')
body.append(b'')
body.append(b'Tamil')
body.append(f"--{boundary}--".encode())
body.append(b'')

payload = b"\r\n".join(body)

# 1. POST /upload
req = urllib.request.Request(
    "http://127.0.0.1:8000/upload",
    data=payload,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST"
)

with urllib.request.urlopen(req) as resp:
    up_data = json.loads(resp.read().decode())
    man_id = up_data["id"]
    print("1. Uploaded Image -> Manuscript ID:", man_id)

# 2. POST /identify-script
req_id = urllib.request.Request(
    "http://127.0.0.1:8000/identify-script",
    data=f"manuscript_id={man_id}".encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req_id) as resp:
    id_data = json.loads(resp.read().decode())
    print("2. Script Identified:", id_data["script"], "(Confidence:", id_data["confidence"], ")")

# 3. POST /ocr (Live Sarvam Call)
req_ocr = urllib.request.Request(
    "http://127.0.0.1:8000/ocr",
    data=f"manuscript_id={man_id}".encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req_ocr) as resp:
    ocr_data = json.loads(resp.read().decode())
    print("3. Live Sarvam OCR Result:")
    print("   Status:", ocr_data["status"])
    print("   Extracted Text:", repr(ocr_data["extracted_text"]))
    print("   Provider:", ocr_data["provider"])

# 4. POST /restore
req_res = urllib.request.Request(
    "http://127.0.0.1:8000/restore",
    data=f"manuscript_id={man_id}".encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req_res) as resp:
    res_data = json.loads(resp.read().decode())
    print("4. Text Restoration Result:")
    print("   Status:", res_data["status"])
    print("   Restored Text:", repr(res_data["restored_text"]))

# 5. POST /convert-modern
req_mod = urllib.request.Request(
    "http://127.0.0.1:8000/convert-modern",
    data=f"manuscript_id={man_id}".encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req_mod) as resp:
    mod_data = json.loads(resp.read().decode())
    print("5. Modern Tamil Result:")
    print("   Status:", mod_data["status"])
    print("   Modern Tamil Text:", repr(mod_data["modern_tamil_text"]))

# 6. POST /translate-english
req_trans = urllib.request.Request(
    "http://127.0.0.1:8000/translate-english",
    data=f"manuscript_id={man_id}".encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST"
)
with urllib.request.urlopen(req_trans) as resp:
    trans_data = json.loads(resp.read().decode())
    print("6. English Translation Result:")
    print("   Status:", trans_data["status"])
    print("   English Translation:", repr(trans_data["english_translation"]))
