import sys
import os
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.restoration_service import SARVAM_API_KEY, SARVAM_CHAT_URL, SARVAM_MODEL

prompt = """You are the Maruthulir Tamil manuscript restoration engine.

RAW OCR OUTPUT:
<<<மரமிசைஏிானமாணடிசேரநதார
வேணடுதலவேணடாைலானடிசேரநதாரககு>>>

ATTESTED CLASSICAL LEXICON CANDIDATES:
- மரமிசைஏிான -> மலர்மிசை ஏகினான்
- மாணடிசேரநதார -> மாணடி சேர்ந்தார்
- வேணடுதலவேணடாை -> வேண்டுதல் வேண்டாமை
- இலானடிசேரநதாரககு -> இலானடி சேர்ந்தார்க்கு

OUTPUT FORMAT:
Return JSON ONLY with exact structure:
{
  "restored_tamil": "மலர்மிசை ஏகினான் மாணடி சேர்ந்தார்\\nவேண்டுதல் வேண்டாமை இலானடி சேர்ந்தார்க்கு",
  "english_translation": "Those who reach the glorious feet of Him who walked upon the lotus heart, and who is free from desire and aversion...",
  "uncertain_terms": []
}
"""

payload = {
    "model": SARVAM_MODEL,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 8192
}

req = urllib.request.Request(
    SARVAM_CHAT_URL,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={
        'api-subscription-key': SARVAM_API_KEY,
        'Content-Type': 'application/json'
    }
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    msg = res['choices'][0]['message']
    print("FINISH REASON:", res['choices'][0].get('finish_reason'))
    print("CONTENT:\n", msg.get('content'))
    print("\nREASONING SNIPPET:\n", (msg.get('reasoning_content') or '')[:300])
