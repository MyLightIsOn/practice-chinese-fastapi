from agents import Agent, function_tool
from typing import List, Dict

# Define a tool to access selected vocabulary words
@function_tool
def get_selected_words(words: List[str]) -> List[Dict[str, str]]:
    """
    Retrieve details about the selected Chinese vocabulary words.

    Args:
        words: List of simplified Chinese characters selected by the user

    Returns:
        List of dictionaries containing details about each word
    """
    return [{"simplified": word, "traditional": word, "pinyin": "pinyin", "definition": f"Definition of {word}"}
            for word in words]


# Exercise Generator Agent
exercise_generator = Agent(
    name="Exercise Generator",
    instructions="""
    You are an expert in creating Chinese language learning exercises.
    Your task is to create exercises based on the provided vocabulary words.

    Exercise types:
    1. Fill in the blank: Create sentences with blanks where the vocabulary words should be used.
    2. Multiple choice: Create questions with 4 options where only one is correct.

    Character types:
    - Traditional: Use traditional Chinese characters in the exercise
    - Simplified: Use simplified Chinese characters in the exercise

    Rules:
    - Use only the provided vocabulary words
    - Create exercises of the type(s) specified in the request
    - Use the character type (traditional or simplified) specified in the request
    - Create clear and concise exercises
    - Ensure the exercises test understanding of the words
    - Provide the correct answers
    """
,
    tools=[get_selected_words],
)