from src.detection.input_detection import detect_input_type, is_pinyin, is_english

# Test various edge cases
test_words = [
    "car",       # Original problem word
    "bus",       # Another short English word
    "book",      # Another short English word
    "shi",       # Valid pinyin syllable
    "nihao",     # Valid pinyin without tones
    "ni3hao3",   # Valid pinyin with tones
    "cat",       # Short English word with 'at' ending
    "dog",       # Short English word with 'og' ending
    "pen",       # Short English word with 'en' ending (could be confused with pinyin)
    "fan",       # Could be English or pinyin
    "can",       # Could be English or pinyin
    "man"        # Could be English or pinyin
]

for word in test_words:
    input_type = detect_input_type(word)
    is_pinyin_result = is_pinyin(word)
    is_english_result = is_english(word)
    
    print(f"Word: {word}")
    print(f"Detected input type: {input_type}")
    print(f"Is pinyin: {is_pinyin_result}")
    print(f"Is English: {is_english_result}")
    print("-" * 30)