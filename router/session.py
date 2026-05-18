from fastapi import APIRouter, HTTPException, Request, Request, status
from uuid import UUID, uuid1
from llm import evaluate_answer, final_evaluation, generate_questions
from schema.session import AnswerSubmitSchema, SessionBase, SessionDisplay



router = APIRouter(prefix="/session", tags=["session"])

# In-memory storage for sessions, replace with DB in production
sessions:dict[str, SessionDisplay] = {}

@router.post("/", response_model=SessionDisplay)
def create_session(request: SessionBase):
    id = str(uuid1())  # Generate a dummy UUID for demonstration
    session_display = SessionDisplay(id=id, job_role=request.job_role, experience=request.experience, current_question_idx =0)
    sessions[id] = session_display
    session_display.questions = generate_questions(session_display)
    return session_display  

@router.get("/", response_model=dict[str, SessionDisplay])
def get_sessions():
    return sessions


@router.get("/{session_id}", response_model=SessionDisplay)
def get_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.post("/sessions/{id}/answers")
async def submit_answers(request:AnswerSubmitSchema, id: str):
    session = sessions.get(id)
    data =  request
    answer = data.answer
    current_question_idx = session.current_question_idx if session else 0

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    # print( "question", session.questions[current_question_idx].question, "answer", answer)
    feedback = evaluate_answer(
        session.questions[current_question_idx].question,
        answer
    )
    # print( "feedback", feedback)
    session.questions[current_question_idx].feedback = feedback
    session.questions[current_question_idx].answer = answer
    session.current_question_idx += 1  

    if session.current_question_idx >= len(session.questions):
        return {"message": "All questions answered", "session": session} 

    return {"question_idx": session.current_question_idx, "feedback": feedback, "session": session}


@router.get("/sessions/{id}/final_report")
def generate_final_report(id: str):
    session = sessions.get(id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    final_report = final_evaluation(session)
    session.final_report = final_report
    return {"message": "Final report generated", "session": session}