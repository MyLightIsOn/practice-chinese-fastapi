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

        # Question words
        'what', 'who', 'where', 'when', 'why', 'how',

        # Common nouns and adjectives
        'hello', 'food', 'good', 'bad', 'new', 'old', 'big', 'small', 'many', 'much',
        'morning', 'evening', 'night', 'day', 'week', 'month', 'year', 'time', 'people',

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

    # Basic pinyin pattern: letters possibly followed by tone numbers 1-4
    pinyin_pattern = r'^[a-zA-Z]+[1-4]?$'

    # First, try to match the entire string as a single pinyin syllable
    if re.match(r'^[a-zA-Z]+[1-4]?$', text):
        return True

    # If the text contains digits 1-4 (tone markers), it's likely pinyin
    if re.search(r'[1-4]', text):
        # Check if it's a valid pinyin pattern with tones
        # Allow for formats like "ni3hao3" without spaces
        if re.match(r'^([a-zA-Z]+[1-4])+$', text):
            return True

    # Check each word in the input if it contains spaces
    if words:
        return all(re.match(pinyin_pattern, word) for word in words)

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

    return False


def is_english(text: str) -> bool:
    """Check if the input contains only English characters, spaces, and punctuation."""
    # If it contains Chinese characters, it's not English
    if contains_chinese(text):
        return False

    # Common English words that should be detected as English
    common_english_words = ['hello', 'food', 'good', 'bad', 'the', 'and', 'for', 'with', 'from',
                            'morning', 'evening', 'night', 'day', 'week', 'month', 'year']

    # If it's a common English word, it's English
    if text.lower() in common_english_words:
        return True

    # If it contains multiple words, check if it looks like an English phrase
    words = text.split()
    if len(words) > 1:
        # If any word is a common English word, likely English
        for word in words:
            if word.lower() in common_english_words:
                return True

        # If it has more than 3 words, likely an English phrase
        if len(words) > 3:
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
    elif is_pinyin(text):
        return "pinyin"
    else:
        return "english"


def remove_tone_numbers(pinyin: str) -> str:
    """Remove tone numbers from pinyin."""
    return re.sub(r'[1-4]', '', pinyin)