import os
import re
import json
import urllib.request
from typing import Dict, Any
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip("'\" \t\r\n")

def _extract_english_translation(raw_text: str) -> str:
    """Extracts clean English translation text from API output."""
    if not raw_text:
        return ""

    try:
        data = json.loads(raw_text.strip(), strict=False)
        if isinstance(data, dict) and "english_translation" in data:
            return str(data["english_translation"]).strip()
    except Exception:
        pass

    for match in re.finditer(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text):
        try:
            data = json.loads(match.group(1).strip(), strict=False)
            if isinstance(data, dict) and "english_translation" in data:
                return str(data["english_translation"]).strip()
        except Exception:
            pass

    # Filter out reasoning or meta headers
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    clean_lines = []
    for l in lines:
        if re.match(r'^(Drafting|Attempt|Critique|Step|Note|Meaning|Translation|The user|Let|Input|Rules|Headline|Reasoning|Analyzing)', l, re.IGNORECASE):
            continue
        cleaned = re.sub(r'[\*\#\_\`]', '', l).strip()
        if cleaned:
            clean_lines.append(cleaned)

    if clean_lines:
        return " ".join(clean_lines)
    return ""

def translate_to_english(modern_tamil_text: str) -> Dict[str, Any]:
    """
    Translates Modern Tamil text to English using Sarvam AI Translation API (or clean fallback).
    Strictly zero fake fallback for empty/failed OCR text.
    """
    if not modern_tamil_text or "OCR unavailable" in modern_tamil_text:
        return {
            "modern_tamil_text": "",
            "english_translation": "",
            "status": "failed",
            "message": "OCR unavailable - manuscript was not processed",
            "provider": "Sarvam AI Translation"
        }

    if SARVAM_API_KEY:
        # 1. Try Sarvam Mayura Translation API
        try:
            url = "https://api.sarvam.ai/translate"
            payload = json.dumps({
                "input": modern_tamil_text,
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

            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                translated = res_data.get("translated_text", "").strip()
                if translated and not re.search(r'let\'s analyze|the user wants|here is', translated, re.I):
                    return {
                        "modern_tamil_text": modern_tamil_text,
                        "english_translation": translated,
                        "status": "completed",
                        "message": "Translation completed via Sarvam AI Mayura",
                        "provider": "Sarvam AI (mayura:v1)"
                    }
        except Exception as err:
            print(f"[Sarvam Translate Warning] Mayura Endpoint error: {err}")

        # 2. Fallback to Sarvam-105b Chat API with strict JSON prompt
        try:
            chat_url = "https://api.sarvam.ai/v1/chat/completions"
            sys_prompt = """You are a professional English translator.
Translate the provided Tamil text into natural, fluent English prose.
Return ONLY a valid JSON object with key 'english_translation'. Do NOT include any reasoning, meta commentary, or thinking.

JSON FORMAT ONLY:
{
  "english_translation": "Natural English translation prose..."
}"""
            user_prompt = f"TAMIL TEXT:\n{modern_tamil_text}\n\nReturn ONLY the JSON object with key 'english_translation'."

            chat_payload = json.dumps({
                "model": "sarvam-105b",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 4096
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
            with urllib.request.urlopen(chat_req, timeout=45) as c_resp:
                c_res = json.loads(c_resp.read().decode("utf-8"))
                msg = c_res.get('choices', [{}])[0].get('message', {})
                c_content = msg.get('content') or ""
                c_reasoning = msg.get('reasoning_content') or ""
                
                translated_text = ""
                for raw in [c_content, c_reasoning, c_content + "\n" + c_reasoning]:
                    if raw.strip():
                        translated_text = _extract_english_translation(raw)
                        if translated_text and len(translated_text) >= 10:
                            break

                if translated_text:
                    return {
                        "modern_tamil_text": modern_tamil_text,
                        "english_translation": translated_text,
                        "status": "completed",
                        "message": "Translation completed via Sarvam Chat API",
                        "provider": "Sarvam AI (sarvam-105b)"
                    }
        except Exception as c_err:
            print(f"[Sarvam Translate Warning] Chat Fallback error: {c_err}")

    return {
        "modern_tamil_text": modern_tamil_text,
        "english_translation": "",
        "status": "failed",
        "message": "Translation service unavailable - missing API key or API call failed",
        "provider": "Sarvam AI Translation"
    }
