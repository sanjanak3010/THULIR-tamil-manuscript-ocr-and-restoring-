import sys
import os
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.restoration_service import SARVAM_API_KEY, SARVAM_CHAT_URL, SARVAM_MODEL, RESTORATION_SYSTEM_PROMPT, get_candidate_words

ocr_text = 'மரமிசைஏிானமாணடிசேரநதார வேணடுதலவேணடாைலானடிசேரநதாரககு'
cands1 = get_candidate_words("மரமிசைஏிான", top_n=3)
cands2 = get_candidate_words("மாணடிசேரநதார", top_n=3)
cands3 = get_candidate_words("வேணடுதலவேணடாை", top_n=3)

grounding_info = [
    f"- OCR fragment 'மரமிசைஏிான' -> Candidates: {cands1}",
    f"- OCR fragment 'மாணடிசேரநதார' -> Candidates: {cands2}",
    f"- OCR fragment 'வேணடுதலவேணடாை' -> Candidates: {cands3}"
]

full_prompt = f"{RESTORATION_SYSTEM_PROMPT}\n\nRAW OCR OUTPUT:\n{ocr_text}\n\n"
full_prompt += "ATTESTED CLASSICAL TAMIL LEXICON CANDIDATES:\n" + "\n".join(grounding_info) + "\n\n"
full_prompt += "Return JSON ONLY starting with {\"restored_tamil\":"

payload = {
    "model": SARVAM_MODEL,
    "messages": [{"role": "user", "content": full_prompt}],
    "temperature": 0.1,
    "max_tokens": 8192
}

req = urllib.request.Request(
    SARVAM_CHAT_URL,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={'api-subscription-key': SARVAM_API_KEY, 'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    msg = res['choices'][0]['message']
    print("--- CONTENT ---")
    print(repr(msg.get('content')))
    print("\n--- REASONING CONTENT (END) ---")
    print(repr((msg.get('reasoning_content') or '')[-400:]))
