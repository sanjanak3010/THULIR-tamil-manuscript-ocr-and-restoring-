import re
import json

sample_model_output = """
The user wants me to act as a restoration engine for a Tamil heritage manuscript platform. I need to process the raw OCR output and produce a clean JSON with restored Tamil text, English translation, and uncertain terms.

Input OCR: மரமிசைஏிானமாணடிசேரநதார
Candidate words: மலர்மிசை ஏகினான், மாணடி சேர்ந்தார்

Here is the JSON response:
```json
{
  "restored_tamil": "மலர்மிசை ஏகினான் மாணடி சேர்ந்தார்
வேண்டுதல் வேண்டாமை இலானடி சேர்ந்தார்க்கு
இருள்சேர் இருவினையும் சேரா இறைவன்
பொருள்சேர் புகழ்புரிந்தார் மாட்டு.",
  "english_translation": "Those who reach the glorious feet of Him who walked upon the lotus heart...",
  "uncertain_terms": []
}
```
"""

def _extract_json_payload(text: str):
    if not text:
        raise ValueError("Empty text received for JSON parsing")

    # 1. Direct parse with strict=False
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

parsed = _extract_json_payload(sample_model_output)
print("SUCCESSFULLY PARSED KEYS:", list(parsed.keys()))
print("RESTORED TAMIL:\n", parsed["restored_tamil"])
