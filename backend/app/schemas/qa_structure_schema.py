from typing import List
from pydantic import BaseModel

# Pydantic models for QA
class QuestionAnswer(BaseModel):
    """Schema for a question and its answer."""
    
    question: str
    answer: str

class QuestionAnswerList(BaseModel):
    """Schema for a list of question and answer pairs."""
    
    qa_list: List[QuestionAnswer]
