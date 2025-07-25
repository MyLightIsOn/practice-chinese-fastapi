import re
import os

# Read the pinyin list from the file
pinyin_list_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'pinyin_list')
with open(pinyin_list_path, 'r') as f:
    content = f.read()
    # Extract the list items from the file content
    # The file format is: pinyin_list = ["a", "ai", ...]
    content = content.replace('pinyin_list = [', '').replace(']', '')
    # Split by commas and clean up each item
    pinyin_list = [item.strip().strip('"\'') for item in content.split(',') if item.strip()]

def contains_chinese(text: str) -> bool:
    """Check if the input contains Chinese characters."""
    # Check for Chinese characters using Unicode code point ranges
    for char in text:
        # CJK Unified Ideographs (Basic Chinese characters)
        if '\u4e00' <= char <= '\u9fff':
            return True
        # CJK Unified Ideographs Extension A
        if '\u3400' <= char <= '\u4dbf':
            return True
        # CJK Unified Ideographs Extension B
        if '\u20000' <= char <= '\u2a6df':
            return True
    return False


def is_pinyin(text: str) -> bool:
    """Check if the input matches pinyin patterns."""
    # First, check if the text is in the pinyin_list
    # For single words without tone numbers
    if ' ' not in text and not re.search(r'[1-4]', text):
        if text.lower() in pinyin_list:
            return True
            
        # Check for multi-syllable pinyin words like "nihao"
        if len(text) > 2:
            # Try to split into potential pinyin syllables
            for i in range(1, len(text)):
                if text[:i].lower() in pinyin_list and text[i:].lower() in pinyin_list:
                    return True
                    
            # Try to split into more than two syllables
            for i in range(1, len(text) - 1):
                for j in range(i + 1, len(text)):
                    if (text[:i].lower() in pinyin_list and 
                        text[i:j].lower() in pinyin_list and 
                        text[j:].lower() in pinyin_list):
                        return True
    
    # For words with tone numbers, remove the tone numbers and check
    if re.search(r'[1-4]', text):
        base_text = re.sub(r'[1-4]', '', text)
        if base_text.lower() in pinyin_list:
            return True
        
        # For formats like "ni3hao3" without spaces, try to split into syllables
        potential_syllables = re.findall(r'[a-zA-Z]+[1-4]?', text)
        all_valid = True
        for syllable in potential_syllables:
            # Remove tone number if present
            base_syllable = re.sub(r'[1-4]$', '', syllable)
            if base_syllable.lower() not in pinyin_list:
                all_valid = False
                break
        
        if all_valid and len(potential_syllables) > 0:
            return True
    
    # For words with spaces, check each word against the pinyin_list
    words = text.split()
    if words:
        all_valid = True
        for word in words:
            # Remove tone numbers if present
            base_word = re.sub(r'[1-4]$', '', word)
            if base_word.lower() not in pinyin_list:
                all_valid = False
                break
        
        if all_valid:
            return True
    
    # If none of the above checks passed, it's not pinyin
    return False


def is_english(text: str) -> bool:
    """Check if the input contains only English characters, spaces, and punctuation."""
    # If it contains Chinese characters, it's not English
    if contains_chinese(text):
        return False
    
    # Common English words that are also valid pinyin syllables
    # These words should be prioritized as English even though they are valid pinyin
    common_english_words_also_pinyin = [
        'can', 'fan', 'man', 'pen'
    ]
    
    # If it's a common English word that's also a valid pinyin syllable, prioritize English
    if text.lower() in common_english_words_also_pinyin:
        return True
        
    # If it's pinyin, it's not English
    if is_pinyin(text):
        return False
        
    # Check for English-specific patterns
    english_patterns = [
        r'[qwrtypsdfghjklzxcvbnm]{3,}',  # 3+ consecutive consonants
        r'[^aeiou]r[^aeiou]',  # 'r' between consonants (like "car")
        r'[^aeiou]l[^aeiou]',  # 'l' between consonants
        r'ck', r'sh', r'th', r'ph', r'gh',  # Common English consonant pairs
        r'[^aeiou]y$',  # Words ending with consonant + 'y'
        r'ed$', r'ing$', r'ly$', r'ment$', r'tion$', r'ness$'  # Common English suffixes
    ]
    
    for pattern in english_patterns:
        if re.search(pattern, text.lower()):
            return True

    # Check if the text contains only English letters, spaces, and common punctuation
    if re.match(r'^[a-zA-Z\s.,;:!?\'"-]+$', text):
        words = text.split()
        # For single words, check additional criteria
        if len(words) == 1 and len(text) > 1:
            # If it has no numbers and is longer than 3 characters, likely English
            if not re.search(r'\d', text) and len(text) > 3:
                return True

            # If it doesn't match typical Pinyin patterns, consider it English
            if not re.match(r'^[a-z]{1,3}[1-4]?$', text.lower()):
                return True
        else:
            # Multiple words are more likely to be English than Pinyin
            return True

    # If we've reached this point, it's not Chinese, not Pinyin, and doesn't match English patterns
    # Since we've already checked for pinyin, we can safely return True
    return True


def detect_input_type(text: str) -> str:
    """Detect the type of input: Chinese, Pinyin, or English."""
    if contains_chinese(text):
        return "chinese"
    
    # Common English words that are also valid pinyin syllables
    # These words should be prioritized as English even though they are valid pinyin
    common_english_words_also_pinyin = [
        'can', 'fan', 'man', 'pen'
    ]
    
    # If it's a common English word that's also a valid pinyin syllable, prioritize English
    if text.lower() in common_english_words_also_pinyin:
        return "english"
    
    # If it's a single word that exactly matches a pinyin syllable, prioritize pinyin
    if text.lower() in pinyin_list:
        return "pinyin"
    
    # If it contains tone numbers, it's definitely pinyin
    if re.search(r'[1-4]', text):
        return "pinyin"
    
    # For other cases, use the regular detection logic
    if is_pinyin(text):
        return "pinyin"
    else:
        return "english"


def remove_tone_numbers(pinyin: str) -> str:
    """Remove tone numbers from pinyin."""
    return re.sub(r'[1-4]', '', pinyin)