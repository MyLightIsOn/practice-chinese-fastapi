from agents import Agent, function_tool
from typing import List, Dict, Literal, Union
from pydantic import BaseModel, Field

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
    # In a real implementation, this would query your dictionary database
    # For now, we'll return a simple mock response
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

    Rules:
    - Use only the provided vocabulary words
    - Create clear and concise exercises
    - Ensure the exercises test understanding of the words
    - Provide the correct answers
    """,
    tools=[get_selected_words],
)

# Evaluator Agent
evaluator = Agent(
    name="Exercise Evaluator",
    instructions="""
    You are an expert Chinese language teacher who evaluates exercises.
    Your task is to review exercises and ensure they:

    1. Contain no mistakes in translations or Chinese usage
    2. Follow the exercise type guidelines
    3. Are appropriate for language learners

    If you find any issues, explain them clearly so they can be fixed.
    If the exercise is correct, approve it for formatting.
    """,
)

class FillInBlankQuestion(BaseModel):
    text: str = Field(..., description="Text with _____ for blanks")

class FillInBlankExercise(BaseModel):
    exercise_type: Literal["fill_in_blank"] = "fill_in_blank"
    questions: List[FillInBlankQuestion]
    answers: List[str] = Field(..., description="Correct answers for each blank")

class MultipleChoiceQuestion(BaseModel):
    text: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="Array of 4 possible answers")

class MultipleChoiceExercise(BaseModel):
    exercise_type: Literal["multiple_choice"] = "multiple_choice"
    questions: List[MultipleChoiceQuestion]
    answers: List[int] = Field(..., description="Indices (0-3) of correct options")

ExerciseOutput = Union[FillInBlankExercise, MultipleChoiceExercise]


# Exercise Formatter Agent
formatter = Agent(
    name="Exercise Formatter",
    instructions="""
    You format exercises into a consistent JSON structure for the frontend to render.

    The JSON structure should include:
    - exercise_type: "fill_in_blank" or "multiple_choice"
    - questions: Array of question objects
    - answers: Array of correct answers

    For fill-in-blank:
    - Each question should have a "text" field with _____ for blanks
    - Each answer should correspond to a blank

    For multiple choice:
    - Each question should have "text" and "options" (array of 4 options)
    - Each answer should be the index of the correct option (0-3)
    """,
    output_type=ExerciseOutput
,
)