import sys
import os
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.translation_service import SARVAM_API_KEY

def test_sarvam_translate():
    print("Testing Sarvam Translate API...")
    url = "https://api.sarvam.ai/translate"
    payload = json.dumps({
        "input": "தமிழ் எழுத்துக்களில் முதல் எழுத்தான அ மற்ற எல்லா எழுத்துகளுக்கும் அடிப்படையாகும்.",
        "source_language_code": "ta-IN",
        "target_language_code": "en-IN",
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": True
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("TRANSLATE RESULT:", res_data)
    except Exception as e:
        print("TRANSLATE API ERROR:", e)
        
        # Test Chat API fallback
        chat_url = "https://api.sarvam.ai/v1/chat/completions"
        chat_payload = json.dumps({
            "model": "sarvam-105b",
            "messages": [
                {"role": "user", "content": "Translate this Tamil text to clear natural English. Return ONLY the English translation text:\nதமிழ் எழுத்துக்களில் முதல் எழுத்தான அ மற்ற எல்லா எழுத்துகளுக்கும் அடிப்படையாகும்."}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }).encode("utf-8")
        
        chat_req = urllib.request.Request(
            chat_url,
            data=chat_payload,
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(chat_req, timeout=15) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            msg = c_res['choices'][0]['message']
            print("CHAT TRANSLATION FALLBACK RESULT:", msg.get('content'))

if __name__ == "__main__":
    test_sarvam_translate()
