import os
import sys
import re
import json
import html
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(PROJECT_ROOT)

CORPUS_RAW_DIR = os.path.join(BASE_DIR, "corpus_raw")
CORPUS_CLEAN_DIR = os.path.join(BASE_DIR, "corpus_clean")
LEXICON_DIR = os.path.join(BASE_DIR, "lexicon")

os.makedirs(CORPUS_CLEAN_DIR, exist_ok=True)
os.makedirs(LEXICON_DIR, exist_ok=True)

def strip_html_and_metadata(raw_html: str) -> str:
    # 1. Remove style and script blocks
    text = re.sub(r'(?is)<style.*?>.*?</style>', '', raw_html)
    text = re.sub(r'(?is)<script.*?>.*?</script>', '', text)
    text = re.sub(r'(?is)<head.*?>.*?</head>', '', text)
    
    # 2. Replace breaks and paragraphs with newline
    text = re.sub(r'(?i)<br\s*/?>', '\n', text)
    text = re.sub(r'(?i)</p>', '\n', text)
    text = re.sub(r'(?i)</div>', '\n', text)
    text = re.sub(r'(?i)</tr>', '\n', text)
    
    # 3. Strip remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 4. Unescape HTML entities
    text = html.unescape(text)
    
    # 5. Clean up non-Tamil web chrome lines where appropriate while retaining Tamil poetry lines
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        # Skip pure header english boilerplate lines
        if re.match(r'^(Project Madurai|Etext|Prepared|Unicode|HTML|HTTP|http|www\.)', line_str, re.IGNORECASE) and not re.search(r'[\u0B80-\u0BFF]', line_str):
            continue
        cleaned_lines.append(line_str)
        
    return '\n'.join(cleaned_lines)

def tokenize_tamil(text: str) -> list[str]:
    # Extract contiguous Tamil unicode sequences (\u0B80-\u0BFF)
    # Filter out single character isolated vowel signs or dots if any non-word occurs
    tokens = re.findall(r'[\u0B80-\u0BFF]+', text)
    # Keep tokens that contain at least one Tamil uyir (0B85-0B94) or uyirmei/mei character (0B95-0BB9)
    valid_tokens = []
    for tok in tokens:
        # Avoid purely isolated diacritic sequences if any
        if any('\u0B85' <= ch <= '\u0BB9' for ch in tok):
            valid_tokens.append(tok)
    return valid_tokens

def process_corpus():
    print("=== PHASE 2: CORPUS CLEANING & LEXICON BUILD ===")
    print(f"Raw Input Dir:   {CORPUS_RAW_DIR}")
    print(f"Clean Output Dir: {CORPUS_CLEAN_DIR}")
    print(f"Lexicon Output:   {LEXICON_DIR}\n")
    
    raw_files = [f for f in os.listdir(CORPUS_RAW_DIR) if f.endswith('.html') or f.endswith('.txt')]
    raw_files.sort()
    
    if not raw_files:
        print("ERROR: No files found in corpus_raw!")
        return
        
    word_counter = Counter()
    total_cleaned_files = 0
    total_tokens_extracted = 0
    file_stats = []
    
    for filename in raw_files:
        raw_path = os.path.join(CORPUS_RAW_DIR, filename)
        with open(raw_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
            
        clean_text = strip_html_and_metadata(raw_content)
        tokens = tokenize_tamil(clean_text)
        
        # Save cleaned file
        clean_filename = os.path.splitext(filename)[0] + ".txt"
        clean_path = os.path.join(CORPUS_CLEAN_DIR, clean_filename)
        with open(clean_path, 'w', encoding='utf-8') as cf:
            cf.write(clean_text)
            
        word_counter.update(tokens)
        total_cleaned_files += 1
        total_tokens_extracted += len(tokens)
        
        file_stats.append({
            "filename": clean_filename,
            "raw_size": len(raw_content),
            "clean_size": len(clean_text),
            "tokens": len(tokens),
            "unique_tokens": len(set(tokens))
        })
        print(f"  ✓ Cleaned {filename} -> {clean_filename} | Tokens: {len(tokens):,} | Unique: {len(set(tokens)):,}")
        
    # Write classical_tamil_lexicon.json
    lexicon_sorted = dict(word_counter.most_common())
    lexicon_path = os.path.join(LEXICON_DIR, "classical_tamil_lexicon.json")
    with open(lexicon_path, 'w', encoding='utf-8') as lf:
        json.dump(lexicon_sorted, lf, ensure_ascii=False, indent=2)
        
    # Create Phase 3 manual lexicon rules (lexicon_pairs.json)
    lexicon_pairs_data = {
        "entries": [
            {"id": 1, "category": "word_segmentation", "source": "தமிழ்மொழிஎன்தாய்மொழி", "target": "தமிழ் மொழி என் தாய் மொழி", "note": "continuous script -> word-segmented"},
            {"id": 2, "category": "word_segmentation", "source": "நான்பள்ளிக்குச்சென்றேன்", "target": "நான் பள்ளிக்குச் சென்றேன்", "note": "continuous script -> word-segmented"},
            {"id": 3, "category": "word_segmentation", "source": "அவன்நன்றாகப்படித்தான்", "target": "அவன் நன்றாகப் படித்தான்", "note": "continuous script -> word-segmented"},
            {"id": 4, "category": "word_segmentation", "source": "மழைபெய்துகொண்டிருந்தது", "target": "மழை பெய்துகொண்டிருந்தது", "note": "continuous script -> word-segmented"},
            {"id": 5, "category": "pulli_restoration", "source": "தமிழ் லக்கணம்", "target": "தமிழ் இலக்கணம்", "note": "missing initial vowel / pulli error"},
            {"id": 6, "category": "pulli_restoration", "source": "மககள்", "target": "மக்கள்", "note": "missing dot (k -> kk)"},
            {"id": 7, "category": "pulli_restoration", "source": "தமிழனாடு", "target": "தமிழ்நாடு", "note": "missing dot on ம்"},
            {"id": 8, "category": "pulli_restoration", "source": "கணன", "target": "கண்", "note": "missing dot / corruption"},
            {"id": 9, "category": "sandhi_split", "source": "மரப்பெட்டி", "target": "மரம் + பெட்டி", "note": "sandhi fusion -> split components"},
            {"id": 10, "category": "sandhi_split", "source": "கோவில்காளை", "target": "கோவில் + காளை", "note": "sandhi compound -> split"},
            {"id": 11, "category": "sandhi_split", "source": "பூம்பாவாய்", "target": "பூ + பாவாய்", "note": "sandhi fusion -> split"},
            {"id": 12, "category": "sandhi_split", "source": "பண்பாடு", "target": "பண்பு + நாடு", "note": "sandhi split"},
            {"id": 13, "category": "numeral_normalization", "source": "௧", "target": "1", "note": "Tamil numeral 1"},
            {"id": 14, "category": "numeral_normalization", "source": "௨", "target": "2", "note": "Tamil numeral 2"},
            {"id": 15, "category": "numeral_normalization", "source": "௩", "target": "3", "note": "Tamil numeral 3"},
            {"id": 16, "category": "numeral_normalization", "source": "௰", "target": "10", "note": "Tamil numeral 10"},
            {"id": 17, "category": "lexical_normalization", "source": "யானை", "target": "யானை", "note": "classical spelling preserved"},
            {"id": 18, "category": "lexical_normalization", "source": "யாண்டு", "target": "ஆண்டு", "note": "archaic word -> modern equivalent"},
            {"id": 19, "category": "lexical_normalization", "source": "நோன்மை", "target": "தவம்", "note": "archaic word -> modern equivalent"},
            {"id": 20, "category": "lexical_normalization", "source": "அரும்பெறல்", "target": "அரிய", "note": "archaic compound -> modern equivalent"}
        ]
    }
    pairs_path = os.path.join(LEXICON_DIR, "lexicon_pairs.json")
    with open(pairs_path, 'w', encoding='utf-8') as pf:
        json.dump(lexicon_pairs_data, pf, ensure_ascii=False, indent=2)

    # Save Phase 2 Report
    report_data = {
        "files_cleaned": total_cleaned_files,
        "total_tokens": total_tokens_extracted,
        "unique_vocab_size": len(word_counter),
        "top_20_words": word_counter.most_common(20),
        "file_stats": file_stats
    }
    report_path = os.path.join(LEXICON_DIR, "phase2_report.json")
    with open(report_path, 'w', encoding='utf-8') as rf:
        json.dump(report_data, rf, ensure_ascii=False, indent=2)

    print("\n=== PHASE 2 SUMMARY ===")
    print(f"Cleaned Corpus Files: {total_cleaned_files}")
    print(f"Total Tamil Tokens:   {total_tokens_extracted:,}")
    print(f"Unique Tamil Vocab:   {len(word_counter):,} forms (Requirement > 5,000)")
    print(f"Lexicon file saved:   {lexicon_path}")
    print(f"Lexicon pairs saved:  {pairs_path}")
    print(f"Phase 2 report saved: {report_path}")

if __name__ == "__main__":
    process_corpus()
