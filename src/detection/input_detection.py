import re

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
    # Common English words that should not be detected as Pinyin
    common_english_words = [
        # Articles
        'a', 'an', 'the',

        # Prepositions
        'in', 'on', 'at', 'to', 'of', 'by', 'for', 'with', 'from', 'about',

        # Conjunctions
        'and', 'but', 'or', 'because', 'if', 'when', 'while',

        # Pronouns
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their',

        # Common verbs
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'go', 'see', 'want', 'know', 'think', 'make', 'take', 'get', 'come', 'say',
        'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must',

        # Question words
        'what', 'who', 'where', 'when', 'why', 'how',

        # Common nouns and adjectives
        'hello', 'food', 'good', 'bad', 'new', 'old', 'big', 'small', 'many', 'much',
        'morning', 'evening', 'night', 'day', 'week', 'month', 'year', 'time', 'people',
        'car', 'bus', 'train', 'bike', 'book', 'pen', 'dog', 'cat', 'man', 'woman', 'boy', 'girl',
        'house', 'home', 'work', 'job', 'school', 'class', 'room', 'door', 'window', 'wall',
        'water', 'food', 'tea', 'coffee', 'milk', 'bread', 'rice', 'meat', 'fish', 'fruit',
        'red', 'blue', 'green', 'yellow', 'black', 'white', 'color', 'hot', 'cold', 'warm',
        'fan', 'run', 'sun', 'fun', 'gun', 'hat', 'bat', 'rat', 'mat', 'sat', 'fat',
        'cup', 'up', 'top', 'stop', 'shop', 'drop', 'hop', 'pop', 'mop', 'cop',

        # Demonstratives and common adverbs
        'this', 'that', 'these', 'those', 'there', 'here', 'now', 'then', 'very', 'too'
    ]

    # If it's a common English word, it's not Pinyin
    if text.lower() in common_english_words:
        return False

    # If it contains multiple words, check if it looks like an English phrase
    words = text.split()
    if len(words) > 1:
        # If any word is a common English word, likely not Pinyin
        for word in words:
            if word.lower() in common_english_words:
                return False

        # If it has more than 3 words, likely an English phrase
        if len(words) > 3:
            return False

    # Check for English-specific patterns (consonant clusters that don't exist in pinyin)
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
            return False

    # If the text contains digits 1-4 (tone markers), it's likely pinyin
    if re.search(r'[1-4]', text):
        # Check if it's a valid pinyin pattern with tones
        # Allow for formats like "ni3hao3" without spaces
        if re.match(r'^([a-zA-Z]+[1-4])+$', text):
            return True

    # For single words without tone numbers, check if it's a valid pinyin syllable
    if len(words) == 0 and not re.search(r'[1-4]', text):
        # Common pinyin syllables without tones
        common_syllables = ['zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'yi', 'wu', 'yu', 'ye', 'yue', 'yuan',
                            'yin', 'yun', 'ying', 'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng',
                            'ni', 'hao', 'ma', 'de', 'le', 'ba', 'ge', 'ne', 'la', 'a', 'ai', 'an', 'ang',
                            'ao', 'e', 'ei', 'en', 'er', 'o', 'ou']

        # If it's a common pinyin syllable, it's Pinyin
        if text.lower() in common_syllables:
            return True
            
        # Check for valid pinyin initial-final combinations
        valid_initials = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']
        valid_finals = ['a', 'o', 'e', 'i', 'u', 'v', 'ai', 'ei', 'ui', 'ao', 'ou', 'iu', 'ie', 'ue', 'er', 'an', 'en', 'in', 'un', 'vn', 'ang', 'eng', 'ing', 'ong']
        
        # If the word doesn't follow pinyin syllable structure, it's not pinyin
        is_valid_pinyin = False
        for initial in valid_initials:
            if text.lower().startswith(initial):
                remainder = text.lower()[len(initial):]
                if remainder in valid_finals:
                    is_valid_pinyin = True
                    break
        
        # Special case for syllables that are just finals
        if not is_valid_pinyin and text.lower() in valid_finals:
            is_valid_pinyin = True
            
        return is_valid_pinyin

    # Basic pinyin pattern: letters possibly followed by tone numbers 1-4
    pinyin_pattern = r'^[a-zA-Z]+[1-4]?$'
    
    # Check each word in the input if it contains spaces
    if words:
        return all(re.match(pinyin_pattern, word) for word in words)

    return False


def is_english(text: str) -> bool:
    """Check if the input contains only English characters, spaces, and punctuation."""
    # If it contains Chinese characters, it's not English
    if contains_chinese(text):
        return False

    # Common English words that should be detected as English
    common_english_words = [
        # Basic words
        'hello', 'food', 'good', 'bad', 'the', 'and', 'for', 'with', 'from',
        'morning', 'evening', 'night', 'day', 'week', 'month', 'year',
        # Transportation
        'car', 'bus', 'train', 'bike', 'walk', 'drive', 'fly', 'travel',
        # Common nouns
        'book', 'pen', 'dog', 'cat', 'man', 'woman', 'boy', 'girl', 'child',
        'house', 'home', 'work', 'job', 'school', 'class', 'room', 'door',
        # Food and drink
        'water', 'tea', 'coffee', 'milk', 'bread', 'rice', 'meat', 'fish', 'fruit'
    ]

    # If it's a common English word, it's English
    if text.lower() in common_english_words:
        return True

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

    # If it contains multiple words, check if it looks like an English phrase
    words = text.split()
    if len(words) > 1:
        # If any word is a common English word, likely English
        for word in words:
            if word.lower() in common_english_words:
                return True

        # If it has more than 2 words, likely an English phrase
        if len(words) > 2:
            return True

    # Check if the text contains only English letters, spaces, and common punctuation
    if re.match(r'^[a-zA-Z\s.,;:!?\'"-]+$', text):
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

    # If it's not Chinese and not Pinyin, we'll consider it English
    return not is_pinyin(text)


def detect_input_type(text: str) -> str:
    """Detect the type of input: Chinese, Pinyin, or English."""
    if contains_chinese(text):
        return "chinese"
    
    # Check for valid pinyin syllables first
    common_syllables = ['zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'yi', 'wu', 'yu', 'ye', 'yue', 'yuan',
                        'yin', 'yun', 'ying', 'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng',
                        'ni', 'hao', 'ma', 'de', 'le', 'ba', 'ge', 'ne', 'la', 'a', 'ai', 'an', 'ang',
                        'ao', 'e', 'ei', 'en', 'er', 'o', 'ou']
    
    # If it's a single word that exactly matches a common pinyin syllable, prioritize pinyin
    if text.lower() in common_syllables:
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