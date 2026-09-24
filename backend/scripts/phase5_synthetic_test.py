import os
import sys
import re
import json
import random
import difflib

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(PROJECT_ROOT)

sys.path.insert(0, PROJECT_ROOT)
from services.restoration_service import restore_tamil_text, get_candidate_words

CORPUS_CLEAN_DIR = os.path.join(BASE_DIR, "corpus_clean")

def corrupt_passage(clean_text: str, noise_level: float = 0.10) -> str:
    """
    Synthetically corrupts clean Tamil text:
    1. Removes pulli (virama) dots (்)
    2. Strips spaces to simulate continuous unspaced manuscript text
    3. Randomly drops or mutates characters (~10% noise)
    """
    # 1. Remove pullis
    text = clean_text.replace("்", "")
    
    # 2. Randomly collapse spaces
    lines = text.splitlines()
    corrupted_lines = []
    for line in lines:
        words = line.split()
        if not words:
            continue
        # Join words without spaces to simulate continuous script
        joined = "".join(words)
        
        # Introduce light character noise (10%)
        chars = list(joined)
        for i in range(len(chars)):
            if random.random() < noise_level:
                # drop or duplicate character
                if random.random() < 0.5 and len(chars) > 5:
                    chars[i] = ""
        corrupted_lines.append("".join(chars))
        
    return "\n".join(corrupted_lines[:4]) # limit to 4 verses/lines per test sample

def calculate_word_accuracy(restored_text: str, ground_truth_text: str) -> float:
    orig_words = set(re.findall(r'[\u0B80-\u0BFF]+', ground_truth_text))
    restored_words = set(re.findall(r'[\u0B80-\u0BFF]+', restored_text))
    if not orig_words:
        return 0.0
    matched = orig_words.intersection(restored_words)
    return round((len(matched) / len(orig_words)) * 100, 2)

def is_tamil_verse_line(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 5:
        return False
    # Count Tamil characters
    tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', line))
    # Line must be predominantly Tamil characters (>70%)
    return (tamil_chars / len(line)) > 0.70

def run_synthetic_test():
    print("=== PHASE 5: SYNTHETIC CORRUPTION TEST SUITE ===")
    
    test_files = ["pmuni0001.txt", "pmuni0002.txt", "pmuni0004.txt"]
    results = []
    
    for fname in test_files:
        fpath = os.path.join(CORPUS_CLEAN_DIR, fname)
        if not os.path.exists(fpath):
            print(f"Skipping missing test file {fname}")
            continue
            
        with open(fpath, 'r', encoding='utf-8') as f:
            full_text = f.read()
            
        # Extract clean Tamil verse lines
        all_lines = full_text.splitlines()
        clean_verse_lines = [l.strip() for l in all_lines if is_tamil_verse_line(l)]
        
        if not clean_verse_lines:
            print(f"No valid Tamil verse lines in {fname}")
            continue
            
        clean_snippet = "\n".join(clean_verse_lines[5:9] if len(clean_verse_lines) >= 9 else clean_verse_lines[:4])
        
        # Corrupt snippet
        random.seed(42)
        corrupted_snippet = corrupt_passage(clean_snippet, noise_level=0.08)
        
        print(f"\n--- Testing on {fname} ---")
        print(f"Original Clean Snippet:\n{clean_snippet}")
        print(f"\nSynthetically Corrupted Snippet:\n{corrupted_snippet}")
        
        # Run restoration
        res = restore_tamil_text(corrupted_snippet)
        restored = res.get("restored_text", "")
        english = res.get("english_translation", "")
        uncertain = res.get("uncertain_terms", [])
        
        accuracy = calculate_word_accuracy(restored, clean_snippet)
        print(f"\nRestored Text Output:\n{restored}")
        print(f"English Translation:\n{english}")
        print(f"Uncertain Terms: {uncertain}")
        print(f"Word Accuracy Score: {accuracy}%")
        
        results.append({
            "file": fname,
            "original": clean_snippet,
            "corrupted": corrupted_snippet,
            "restored": restored,
            "english": english,
            "word_accuracy": accuracy
        })
        
    avg_accuracy = round(sum(r["word_accuracy"] for r in results) / max(len(results), 1), 2)
    print("\n=== SYNTHETIC CORRUPTION TEST SUMMARY ===")
    print(f"Samples Tested: {len(results)}")
    print(f"Average Word Reconstruction Accuracy: {avg_accuracy}%")
    
    report_path = os.path.join(BASE_DIR, "lexicon", "phase5_synthetic_report.json")
    with open(report_path, 'w', encoding='utf-8') as rf:
        json.dump({"results": results, "average_accuracy": avg_accuracy}, rf, ensure_ascii=False, indent=2)
    print(f"Test report saved to {report_path}")


if __name__ == "__main__":
    run_synthetic_test()
