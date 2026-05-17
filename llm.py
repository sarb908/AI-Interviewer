from langchain_openai import ChatOpenAI
from prompts import generate_questions_prompt
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question text")
    answer: str = Field(default="", description="Leave empty string")
    feedback: str = Field(default="", description="Leave empty string")

class QuestionGenerationResponse(BaseModel):
    questions: List[InterviewQuestion] = Field(description="List of 5 generated interview questions")


llm = ChatOpenAI(model = "gpt-4o", api_key =OPENAI_API_KEY )
res = llm.invoke("hi")
llm = llm.with_structured_output(QuestionGenerationResponse)

print(res.content)


def generate_questions(session_display):
    chain = generate_questions_prompt | llm 
    res = chain.invoke({
        "job_role": session_display.job_role,
        "experience": session_display.experience
    })
    print(res.questions)
    return res.questions