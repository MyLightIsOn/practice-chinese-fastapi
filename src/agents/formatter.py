from agents import Agent
from typing import List, Literal, Union
from pydantic import BaseModel, Field

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
    You are an expert in formatting Chinese language exercises for display in a web application.
    Your task is to take approved exercises and format them for frontend rendering.
    
    Pay attention to:
    - Format the exercise according to its type (fill in the blank or multiple choice)
    - Use the specified character type (traditional or simplified) in the formatted output
    - Structure the data in a way that's easy for the frontend to render
    - Include all necessary information (questions, options, correct answers)
    
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
    output_type=ExerciseOutput,
)