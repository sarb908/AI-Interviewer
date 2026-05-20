from pydantic import BaseModel, Field
from typing import List, Optional



class SessionBase(BaseModel):
    id: Optional[str] = None
    job_role: str = Field(..., example="Software Engineer")
    experience: Optional[int] = Field(default=0, example=5) 
    questions: Optional[List[dict]] = None
    current_question_idx: Optional[int] = 0
    final_report: Optional[str] = None


class CreateSessionRequest(BaseModel):
    job_role: str = Field(..., example="React Developer")
    experience: int = Field(..., ge=0, le=50, example=2)

class SessionDisplay(BaseModel):
    id: str
    job_role: str
    experience: int
    questions: List[str]
    current_question_idx: Optional[int] = 0
    final_report: Optional[str] = None


class AnswerSubmitSchema(BaseModel):
    answer: str

class SubmitAnswerResponse(BaseModel):
    id:str
    current_question_idx: int
    question: str
    feedback: str
    next_question_idx: Optional[int] = None
    next_question: Optional[str] = None
    questions:List[str]
