from pydantic import BaseModel
from typing import List

class ImageCoordinate(BaseModel):
    name: str
    description: str
    box_2d: List[int]

class MarkdownExtraction(BaseModel):
    markdown: str

class ImageCoordinatesExtraction(BaseModel):
    images: List[ImageCoordinate]

# Legacy combined schema (kept for reference)
class PageDigitization(BaseModel):
    markdown: str
    images: List[ImageCoordinate]

class ProblemSolution(BaseModel):
    problem_description: str
    solution_steps: List[str]
    final_answer: str

class PageSolving(BaseModel):
    solutions: List[ProblemSolution]
