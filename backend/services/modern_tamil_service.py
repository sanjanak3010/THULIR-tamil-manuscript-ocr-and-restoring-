import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip("'\" \t\r\n")
SARVAM_CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-105b"

MODERN_TAMIL_SYSTEM_PROMPT = """You are an expert Tamil scholar and linguist.
Your task is to take the provided restored Classical Tamil manuscript text and rewrite its complete meaning into ONE continuous, fluent, simple Modern Tamil prose paragraph suitable for school and college students (தற்கால எளிய தமிழ் உரைநடைப் பத்தி).

STRICT RULES:
1. Output MUST be valid JSON ONLY with key "modern_tamil_paragraph".
2. The value of "modern_tamil_paragraph" MUST be a single continuous Tamil prose paragraph explaining the overall meaning of the text.
3. 100% contemporary Tamil prose. Absolutely NO English words, NO English commentary, NO system prompts, NO word-by-word dictionary explanations, NO quotes, NO bullet points, NO line breaks.
4. Do NOT invent new historical facts or people not present in the manuscript.

JSON FORMAT ONLY:
{
  "modern_tamil_paragraph": "ஒரு தொடர்ச்சியான எளிய தற்கால தமிழ் உரைநடை பத்தி..."
}"""

PROMPT_SIGNATURES = [
    "your task is",
    "you are an expert",
    "classical/medieval tamil",
    "strict rules",
    "return exactly one",
    "do not include",
    "modern tamil paragraph",
    "classical tamil text",
    "contemporary tamil paragraph",
    "school and college students",
    "analyze the user",
    "here is the modern tamil",
    "the given text",
    "this inscription",
    "the original text",
    "this passage",
    "the translated text",
    "meaning:",
    "translation:",
    "summary:",
    "note:",
    "likely referring to",
    "word-by-word",
    "உங்கள் பணி",
    "கண்டிப்பான விதிகள்"
]

def contains_prompt_leakage(text: str) -> bool:
    """Checks if output contains system instruction, prompt text, or meta phrases."""
    if not text:
        return False
    lower_text = text.lower()
    for sig in PROMPT_SIGNATURES:
        if sig in lower_text:
            return True
    return False

def is_valid_modern_tamil_paragraph(text: str) -> bool:
    """
    Strictly validates that output is substantial, fully in Tamil script,
    contains no English commentary/words/prompts, and is a single continuous paragraph.
    """
    if not text or not text.strip():
        return False

    cleaned = text.strip()

    # 1. Reject any text containing system prompt signatures or preamble phrases
    if contains_prompt_leakage(cleaned):
        return False

    # Count Tamil characters and English letters
    tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', cleaned))
    english_letters = len(re.findall(r'[a-zA-Z]', cleaned))

    # 2. Must contain substantial Tamil text (>= 15 Tamil characters)
    if tamil_chars < 15:
        return False

    # 3. Must NOT contain English explanatory/commentary text or English words (> 3 English letters)
    if english_letters > 3:
        return False

    # 4. Ratio of Tamil characters to total letter characters must be at least 90%
    total_letters = tamil_chars + english_letters
    if (tamil_chars / total_letters) < 0.90:
        return False

    # 5. Must be a single continuous paragraph
    if len(cleaned.splitlines()) > 1:
        return False

    return True

def _extract_json_paragraph(raw_text: str) -> str:
    """Extracts modern_tamil_paragraph from JSON or candidate text string."""
    if not raw_text:
        return ""

    # Direct JSON parse
    try:
        data = json.loads(raw_text.strip(), strict=False)
        if isinstance(data, dict) and "modern_tamil_paragraph" in data:
            return str(data["modern_tamil_paragraph"]).strip()
    except Exception:
        pass

    # Markdown fence blocks
    for match in re.finditer(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text):
        block = match.group(1).strip()
        try:
            data = json.loads(block, strict=False)
            if isinstance(data, dict) and "modern_tamil_paragraph" in data:
                return str(data["modern_tamil_paragraph"]).strip()
        except Exception:
            pass

    # Search for candidate JSON substring
    open_indices = [i for i, ch in enumerate(raw_text) if ch == '{']
    close_indices = [i for i, ch in enumerate(raw_text) if ch == '}']
    for start in reversed(open_indices):
        for end in reversed(close_indices):
            if end > start:
                try:
                    cand_str = raw_text[start:end+1]
                    data = json.loads(cand_str, strict=False)
                    if isinstance(data, dict) and "modern_tamil_paragraph" in data:
                        return str(data["modern_tamil_paragraph"]).strip()
                except Exception:
                    pass

    return ""

def _call_sarvam_modern_tamil(text: str) -> str:
    """Invokes Sarvam-105b Chat Completion API to generate Modern Tamil prose paragraph."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is missing from backend/.env configuration.")

    user_prompt = f"RESTORED CLASSICAL TAMIL TEXT:\n{text.strip()}\n\nReturn ONLY the JSON object with key 'modern_tamil_paragraph'."

    payload = {
        "model": SARVAM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": MODERN_TAMIL_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 8192
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        SARVAM_CHAT_URL,
        data=data,
        headers={
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            res_body = response.read().decode("utf-8")
            result = json.loads(res_body)

        msg = result.get("choices", [{}])[0].get("message", {})
        raw_content = msg.get("content") or ""
        raw_reasoning = msg.get("reasoning_content") or ""

        # Try extracting JSON payload from content first, then reasoning, then combined
        modern_text = ""
        for raw in [raw_content, raw_reasoning, raw_content + "\n" + raw_reasoning]:
            if raw.strip():
                modern_text = _extract_json_paragraph(raw)
                if modern_text and is_valid_modern_tamil_paragraph(modern_text):
                    return modern_text

        # If direct JSON key parsing didn't find valid text, validate extracted string if available
        if modern_text and is_valid_modern_tamil_paragraph(modern_text):
            return modern_text

        raise RuntimeError("Modern Tamil conversion failed: Model output did not meet strict Tamil paragraph validation standards.")

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Sarvam API HTTP Error {e.code}: {err_msg}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error connecting to Sarvam API: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Modern Tamil conversion error: {str(e)}")

def convert_to_modern_tamil(restored_text: str) -> Dict[str, Any]:
    """
    Main function used by Maruthulir backend to convert Classical/Restored Tamil text
    into clear Modern Tamil prose for students.
    """
    if not restored_text or not restored_text.strip():
        return {
            "original_restored_text": "",
            "modern_tamil_text": "",
            "status": "failed",
            "message": "Restored Tamil text is unavailable."
        }

    clean_input = restored_text.strip()
    placeholder_tokens = ["<restored tamil text>", "restored tamil text", "சீரமைக்கப்பட்ட பண்டைய தமிழ் உரை", "restored_tamil"]
    is_placeholder = any(p in clean_input.lower() for p in placeholder_tokens)
    has_tamil = len(re.findall(r'[\u0B80-\u0BFF]', clean_input)) >= 3

    if is_placeholder or not has_tamil:
        return {
            "original_restored_text": restored_text,
            "modern_tamil_text": "",
            "status": "failed",
            "message": "Valid restored Tamil text is unavailable."
        }

    try:
        modern_text = _call_sarvam_modern_tamil(clean_input)
        return {
            "original_restored_text": restored_text,
            "modern_tamil_text": modern_text,
            "status": "completed",
            "message": "Modern Tamil simplification completed using Sarvam-105B."
        }
    except Exception as e:
        print(f"[Modern Tamil Error] {e}")
        return {
            "original_restored_text": restored_text,
            "modern_tamil_text": "",
            "status": "failed",
            "message": f"Modern Tamil conversion failed: {str(e)}"
        }
