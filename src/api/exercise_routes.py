from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Literal

from src.config import OPENAI_API_KEY
from agents import Runner
from src.agents import exercise_generator, evaluator, formatter

router = APIRouter()


class WordRequest(BaseModel):
    word: str
    exercise_type: Literal["fill in the blank", "multiple choice"]
    type: Literal["traditional", "simplified"]

class ExerciseRequest(BaseModel):
    words: List[WordRequest]

@router.post("/generate-exercise", response_model=Dict[str, Any])
async def generate_exercise(request: ExerciseRequest):
    """
    Generate a language learning exercise based on selected vocabulary words.

    Args:
        request: Request containing the list of selected words

    Returns:
        JSON-formatted exercise ready for frontend rendering
    """
    print(f"Received request: {request.words}")

    try:
        # Extract word information
        words = [item.word for item in request.words]
        exercise_types = list(set(item.exercise_type for item in request.words))
        character_type = request.words[0].type  # We'll use the first item's type for consistency

        # Create a structured prompt for the exercise generator
        prompt = f"""
                Create an exercise using these words: {', '.join(words)}
                Exercise type(s): {', '.join(exercise_types)}
                Character type: {character_type}
                """

        # Step 1: Generate exercise with the Exercise Generator agent
        generator_result = await Runner.run(
            exercise_generator,
            prompt
        )

        # Step 2: Evaluate the exercise with the Evaluator agent
        evaluator_result = await Runner.run(
            evaluator,
            f"Evaluate this exercise: {generator_result.final_output}"
        )

        # If the evaluator found issues, regenerate the exercise
        if "issues" in evaluator_result.final_output.lower() or "mistake" in evaluator_result.final_output.lower():
            # Regenerate with feedback
            generator_result = await Runner.run(
                exercise_generator,
                f"Create an exercise using these words: {', '.join(request.words)}. " +
                f"Fix these issues: {evaluator_result.final_output}"
            )

            # Re-evaluate
            evaluator_result = await Runner.run(
                evaluator,
                f"Evaluate this exercise: {generator_result.final_output}"
            )

        # Step 3: Format the exercise with the Formatter agent
        formatter_result = await Runner.run(
            formatter,
            f"Format this approved exercise for the frontend: {generator_result.final_output}"
        )

        # Return the formatted exercise as a dictionary
        return formatter_result.final_output.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating exercise: {str(e)}")