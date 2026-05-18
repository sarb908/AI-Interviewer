from pydantic import BaseModel, Field
from typing import List, Optional



class SessionBase(BaseModel):
    id: Optional[str] = None
    job_role: str = Field(..., example="Software Engineer")
    experience: Optional[int] = Field(default=0, example=5) 
    questions: Optional[List[dict]] = None
    current_question_idx: Optional[int] = 0
    final_report: Optional[str] = None



class SessionDisplay(BaseModel):
    id: str
    job_role: str
    experience: int
    questions: Optional[List[dict]] = None
    current_question_idx: Optional[int] = 0
    final_report: Optional[str] = None


class AnswerSubmitSchema(BaseModel):
    answer: str