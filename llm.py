from langchain_openai import ChatOpenAI
from prompts import generate_questions_prompt, answer_prompt, final_prompt
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
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





def generate_questions(session_display):
    llm = ChatOpenAI(model = "gpt-4o", api_key =OPENAI_API_KEY )
    llm = llm.with_structured_output(QuestionGenerationResponse)
    chain = generate_questions_prompt | llm 
    res = chain.invoke({
        "job_role": session_display.job_role,
        "experience": session_display.experience

    })

    print(res.questions)
    return res.questions


def evaluate_answer(question, answer):
    llm = ChatOpenAI(model = "gpt-4o", api_key =OPENAI_API_KEY )
    chain = answer_prompt | llm 
    res = chain.invoke({
        "question": question,
        "answer": answer
    })
    print(res.content.strip())
    return res.content.strip()


def final_evaluation(session_display):
    # Implement a final evaluation of the candidate based on all questions and answers
    llm = ChatOpenAI(model = "gpt-4o", api_key =OPENAI_API_KEY )
    chain = final_prompt | llm
    res = chain.invoke({
        "data": session_display.questions
    })
    return res.content.strip()      



