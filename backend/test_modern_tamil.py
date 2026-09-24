import os
import sys
import json
import io

# Force UTF-8 stdout for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from services.modern_tamil_service import convert_to_modern_tamil, contains_prompt_leakage

def test_modern_tamil_conversion():
    print("=" * 70)
    print("  MARUTHULIR - MODERN TAMIL CONVERSION ISOLATED & SAFETY TEST  ")
    print("=" * 70)

    # Actual restored manuscript text extracted from Sarvam OCR + Lexicon restoration
    actual_restored_text = """
    உளடலுண்ஙகவிவேரோடெநநெருசுங் கூடுவ ன ப சுவாமி யவரை யுணரும் வாட்டியன் வள்ளி முரசு ழலரி ா மாதா அங்கணா வல்ல நேயசெயசுவறாது புலியோர்
    """

    print("\n1. Testing Modern Tamil conversion with ACTUAL restored manuscript text...")
    res = convert_to_modern_tamil(actual_restored_text)
    modern_text = res["modern_tamil_text"]

    print("   Status:", res["status"])
    print("   Message:", res["message"])
    print("   Modern Tamil Output:\n  ", modern_text)

    # 1. Status assertion
    assert res["status"] == "completed", f"Conversion failed: {res.get('message')}"
    # 2. Output non-empty assertion
    assert modern_text and len(modern_text) > 0, "Modern Tamil text is empty!"
    # 3. Prompt leakage safety assertions
    assert not contains_prompt_leakage(modern_text), "Prompt leakage detected in output!"
    assert "Your task is" not in modern_text, "Instruction string 'Your task is' appeared in output!"
    assert "Classical/Medieval Tamil" not in modern_text, "System prompt string appeared in output!"
    assert "STRICT RULES" not in modern_text, "System prompt rules appeared in output!"
    # 4. Single continuous paragraph assertion
    assert len(modern_text.splitlines()) <= 1, "Output contains multiple lines instead of a single continuous paragraph!"
    # 5. Quotation marks assertion
    assert not (modern_text.startswith('"') and modern_text.endswith('"')), "Output is wrapped in quotes!"
    assert not (modern_text.startswith('“') and modern_text.endswith('”')), "Output is wrapped in quotes!"

    print("\n2. Testing Safety check with prompt input (Simulated prompt leakage)...")
    fake_leakage = "Your task is to convert Classical/Medieval Tamil text into simple modern Tamil."
    assert contains_prompt_leakage(fake_leakage) == True, "contains_prompt_leakage failed to catch prompt leakage!"

    print("\n" + "=" * 70)
    print("  ✅ ALL MODERN TAMIL SAFETY & CONVERSION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_modern_tamil_conversion()