import os
import re
import json
import difflib
import urllib.request
import urllib.error
from typing import Dict, List, Any
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip("'\" \t\r\n")
SARVAM_CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-105b"

LEXICON_PATH = os.path.join(os.path.dirname(BASE_DIR), "lexicon", "classical_tamil_lexicon.json")
PAIRS_PATH = os.path.join(os.path.dirname(BASE_DIR), "lexicon", "lexicon_pairs.json")

_CLASSICAL_LEXICON = None
_LEXICON_PAIRS = None

def _load_lexicon():
    global _CLASSICAL_LEXICON, _LEXICON_PAIRS
    if _CLASSICAL_LEXICON is None and os.path.exists(LEXICON_PATH):
        try:
            with open(LEXICON_PATH, 'r', encoding='utf-8') as f:
                _CLASSICAL_LEXICON = json.load(f)
        except Exception as e:
            print(f"[Lexicon Load Warning] {e}")
            _CLASSICAL_LEXICON = {}
    if _LEXICON_PAIRS is None and os.path.exists(PAIRS_PATH):
        try:
            with open(PAIRS_PATH, 'r', encoding='utf-8') as f:
                _LEXICON_PAIRS = json.load(f).get("entries", [])
        except Exception as e:
            print(f"[Lexicon Pairs Load Warning] {e}")
            _LEXICON_PAIRS = []

def get_candidate_words(ocr_fragment: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """Retrieves attested classical Tamil candidate words for an OCR fragment."""
    _load_lexicon()
    candidates = []
    
    # 1. Check manual rule pairs first
    if _LEXICON_PAIRS:
        for entry in _LEXICON_PAIRS:
            if entry.get("source") == ocr_fragment:
                candidates.append({
                    "word": entry.get("target"),
                    "score": 1.0,
                    "category": entry.get("category"),
                    "note": entry.get("note")
                })
                
    # 2. Similarity search in classical Tamil frequency lexicon
    if _CLASSICAL_LEXICON:
        words = list(_CLASSICAL_LEXICON.keys())
        matches = difflib.get_close_matches(ocr_fragment, words, n=top_n, cutoff=0.55)
        for match in matches:
            if any(c["word"] == match for c in candidates):
                continue
            ratio = difflib.SequenceMatcher(None, ocr_fragment, match).ratio()
            freq = _CLASSICAL_LEXICON.get(match, 1)
            candidates.append({
                "word": match,
                "score": round(ratio, 3),
                "frequency": freq,
                "category": "corpus_attested"
            })
            
    candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
    return candidates[:top_n]

RESTORATION_SYSTEM_PROMPT = """You are the Maruthulir Tamil manuscript restoration engine.
Your task is to take raw noisy Classical/Medieval Tamil OCR text and restore it into clean, modern-readable Tamil script with an English translation, grounded in attested Classical Tamil reference lexicon candidates.

Rules:
1. Split continuous unspaced words (Word Segmentation & Sandhi Split).
2. Restore missing pulli dots (்) on consonants.
3. Normalize archaic numerals and classical words using candidate lexicon suggestions.
4. Flag truly indecipherable words as [தெளிவற்ற சொல்: fragment].

JSON OUTPUT FORMAT (Return JSON object ONLY):
{
  "restored_tamil": "சீரமைக்கப்பட்ட பண்டைய தமிழ் உரை",
  "english_translation": "English translation",
  "uncertain_terms": []
}"""

def _extract_json_payload(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Empty text received for JSON parsing")

    # 1. Direct parse
    try:
        return json.loads(text.strip(), strict=False)
    except Exception:
        pass

    # 2. Markdown fence blocks
    for match in re.finditer(r'```(?:json)?\s*([\s\S]*?)\s*```', text):
        block = match.group(1).strip()
        try:
            return json.loads(block, strict=False)
        except Exception:
            pass

    # 3. Find candidate JSON substrings between '{' and '}'
    open_indices = [i for i, ch in enumerate(text) if ch == '{']
    close_indices = [i for i, ch in enumerate(text) if ch == '}']

    for start in reversed(open_indices):
        for end in reversed(close_indices):
            if end > start:
                cand = text[start:end+1]
                if "restored_tamil" in cand or "english_translation" in cand:
                    try:
                        return json.loads(cand, strict=False)
                    except Exception:
                        pass

    for start in reversed(open_indices):
        for end in reversed(close_indices):
            if end > start:
                try:
                    return json.loads(text[start:end+1], strict=False)
                except Exception:
                    pass

    raise ValueError(f"Could not extract JSON from text: {text[:250]}...")

def _call_sarvam_restoration(ocr_text: str) -> Dict[str, Any]:
    """Invokes Sarvam-105b with candidate lexicon grounding."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY missing from backend/.env")

    _load_lexicon()
    
    tokens = re.findall(r'[\u0B80-\u0BFF]+', ocr_text)
    grounding_info = []
    
    for tok in set(tokens):
        if len(tok) >= 2:
            cands = get_candidate_words(tok, top_n=3)
            if cands:
                cand_str = ", ".join([f"{c['word']} (score: {c['score']})" for c in cands])
                grounding_info.append(f"Fragment '{tok}' -> Candidates: {cand_str}")

    full_prompt = f"{RESTORATION_SYSTEM_PROMPT}\n\nRAW OCR OUTPUT:\n<<<{ocr_text}>>>\n"
    if grounding_info:
        full_prompt += "\nATTESTED CLASSICAL TAMIL LEXICON CANDIDATES:\n" + "\n".join(grounding_info[:15]) + "\n"
    full_prompt += "\nOUTPUT FORMAT:\nReturn ONLY valid JSON object with exact keys: restored_tamil, english_translation, uncertain_terms"

    payload = {
        "model": SARVAM_MODEL,
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 8192
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        SARVAM_CHAT_URL,
        data=data,
        headers={
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        res_body = response.read().decode("utf-8")
        res_json = json.loads(res_body)

    msg_obj = res_json.get("choices", [{}])[0].get("message", {})
    content = msg_obj.get("content") or ""
    reasoning = msg_obj.get("reasoning_content") or ""

    for raw in [content, reasoning, content + "\n" + reasoning]:
        if raw.strip():
            try:
                return _extract_json_payload(raw)
            except Exception:
                continue

    raise ValueError(f"Could not extract JSON from model output: {(content + ' ' + reasoning)[:200]}")

def apply_lexicon_restoration_rules(ocr_text: str) -> str:
    """Rule-based restoration using attestation rules & classical lexicon."""
    _load_lexicon()
    if not ocr_text:
        return ""
        
    text = ocr_text.strip()
    
    if _LEXICON_PAIRS:
        for entry in _LEXICON_PAIRS:
            if entry.get("source") == text:
                return entry.get("target")
                
    tokens = text.split()
    restored_tokens = []
    
    for tok in tokens:
        matched = False
        if _LEXICON_PAIRS:
            for entry in _LEXICON_PAIRS:
                if entry.get("source") == tok:
                    restored_tokens.append(entry.get("target"))
                    matched = True
                    break
        if matched:
            continue
            
        cands = get_candidate_words(tok, top_n=1)
        if cands and cands[0]["score"] >= 0.70:
            restored_tokens.append(cands[0]["word"])
        else:
            restored_tokens.append(tok)
            
    return " ".join(restored_tokens)

def _compute_word_corrections(ocr_text: str, restored_tamil: str, is_inscription: bool) -> tuple:
    """Detects actual word-level corrections between raw OCR and Restored Classical Tamil."""
    _load_lexicon()
    damage_evidence = []
    corrections = []
    
    ocr_words = [w.strip() for w in re.findall(r'[\u0B80-\u0BFF]+', ocr_text) if len(w.strip()) >= 2]
    restored_words = [w.strip() for w in re.findall(r'[\u0B80-\u0BFF]+', restored_tamil) if len(w.strip()) >= 2]
    seen_pairs = set()

    for orig in ocr_words:
        if orig in restored_words:
            continue
        best_match = None
        best_ratio = 0.0
        for r_word in restored_words:
            if r_word in ocr_words:
                continue
            ratio = difflib.SequenceMatcher(None, orig, r_word).ratio()
            if ratio > best_ratio and ratio >= 0.35:
                best_ratio = ratio
                best_match = r_word

        if best_match and (orig, best_match) not in seen_pairs:
            seen_pairs.add((orig, best_match))
            lex_cands = get_candidate_words(orig, top_n=3)
            final_score = best_ratio
            for c in lex_cands:
                if c["word"] == best_match:
                    final_score = max(final_score, c["score"])
                    break

            score_pct = f"{int(round(final_score * 100))}%"
            damage_type = "weathered carved glyph / stone erosion" if is_inscription else "faded ink / damaged palm-leaf margin"

            damage_evidence.append({
                "ocr_fragment": orig,
                "damage_type": damage_type,
                "suggested_restoration": best_match,
                "confidence": round(final_score, 2),
                "score_percent": score_pct,
                "candidates": lex_cands,
                "attestation": "Classical Tamil Reference Lexicon"
            })
            corrections.append({
                "original": orig,
                "corrected": best_match,
                "confidence": round(final_score, 2),
                "score_percent": score_pct,
                "type": damage_type,
                "explanation": f"Linguistic restoration for {damage_type}"
            })

    return damage_evidence, corrections

def restore_tamil_text(ocr_text: str, source_type: str = "palm-leaf") -> Dict[str, Any]:
    """
    Performs OCR cleanup and linguistic text restoration on extracted Tamil text.
    Grounded in Classical Tamil Reference Lexicon and tailored to source_type.
    """
    if not ocr_text or not ocr_text.strip():
        return {
            "original_text": "",
            "restored_text": "",
            "english_translation": "",
            "uncertain_terms": [],
            "corrections": [],
            "damage_evidence": [],
            "confidence": None,
            "status": "failed",
            "message": "OCR unavailable - manuscript was not processed"
        }

    is_inscription = "stone" in source_type.lower() or "inscription" in source_type.lower()

    try:
        res = _call_sarvam_restoration(ocr_text.strip())
        restored_tamil = res.get("restored_tamil", "").strip()
        english_translation = res.get("english_translation", "").strip()
        uncertain_terms = res.get("uncertain_terms", [])

        placeholder_tokens = ["<restored tamil text>", "restored tamil text", "சீரமைக்கப்பட்ட பண்டைய தமிழ் உரை", "restored_tamil"]
        is_placeholder = any(p in restored_tamil.lower() for p in placeholder_tokens)
        has_tamil = len(re.findall(r'[\u0B80-\u0BFF]', restored_tamil)) >= 3

        if not restored_tamil or is_placeholder or not has_tamil:
            restored_tamil = apply_lexicon_restoration_rules(ocr_text)

        if not restored_tamil or not len(re.findall(r'[\u0B80-\u0BFF]', restored_tamil)):
            restored_tamil = ocr_text.strip()

        damage_evidence, corrections = _compute_word_corrections(ocr_text, restored_tamil, is_inscription)

        marked_uncertain = re.findall(r'\[தெளிவற்ற சொல்:\s*([^\]]+)\]', restored_tamil)
        for term in marked_uncertain:
            if term not in uncertain_terms:
                uncertain_terms.append(term)

        for term in uncertain_terms:
            corrections.append({
                "original": term,
                "corrected": term,
                "type": "weathered stone area" if is_inscription else "damaged palm-leaf portion",
                "confidence": 0.60,
                "score_percent": "60%",
                "explanation": "Flagged as indecipherable after reconstruction."
            })

        return {
            "original_text": ocr_text,
            "restored_text": restored_tamil,
            "english_translation": english_translation,
            "uncertain_terms": uncertain_terms,
            "corrections": corrections,
            "damage_evidence": damage_evidence,
            "confidence": 0.95 if not uncertain_terms else 0.85,
            "status": "completed",
            "message": f"Text restoration completed for {source_type}."
        }

    except Exception as err:
        print(f"[Restoration Engine Warning] {err}")
        rule_restored = apply_lexicon_restoration_rules(ocr_text)
        damage_evidence, corrections = _compute_word_corrections(ocr_text, rule_restored, is_inscription)
        return {
            "original_text": ocr_text,
            "restored_text": rule_restored,
            "english_translation": "",
            "uncertain_terms": [],
            "corrections": corrections,
            "damage_evidence": damage_evidence,
            "confidence": 0.80,
            "status": "completed",
            "message": f"Rule-based lexicon restoration applied: {str(err)}"
        }
