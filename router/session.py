import os
from io import BytesIO
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import Response
from uuid import  uuid4
from schema.session import AnswerSubmitSchema, CreateSessionRequest, SessionDisplay, SubmitAnswerResponse, TTSRequest
from llm_langgraph import compiled_graph, InterviewState  , evaluate_answer  , generate_final_report
from openai import OpenAI
from dotenv import load_dotenv
from dependencies.auth import get_current_user


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


router = APIRouter(prefix="/sessions", tags=["session"], dependencies=[Depends(get_current_user)])



@router.post("", response_model=SessionDisplay, status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new interview session using LangGraph workflow."""
    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    # Initial state for the workflow
    initial_state: InterviewState = {
        "job_role": request.job_role,
        "experience": request.experience,
        "data": [],
        "current_question_idx": 0,
        "interview_complete": False,
        "final_report": "",
        "last_question": "",
        "last_answer": None
    }
    
    # Run the workflow up to ask_question
    compiled_graph.invoke(initial_state, config=config)
    
    # Get the current state
    state =  compiled_graph.get_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=500, detail="Failed to initialize session")
    
    values = state.values
    questions = [row["question"] for row in values.get("data", [])]
    
    return SessionDisplay(
        id=session_id,
        job_role=values["job_role"],
        experience=values["experience"],
        questions=questions,
        current_question_idx=values.get("current_question_idx", 0),
    )



@router.get("/{session_id}", response_model=InterviewState)
def get_session(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = compiled_graph.get_state(config)
    values = state.values

    if not values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return InterviewState(
        job_role=values["job_role"],
        experience=values["experience"],
        data=values["data"],
        current_question_idx=values["current_question_idx"],
        interview_complete=values["interview_complete"],
        final_report=values["final_report"],
        last_question=values["last_question"],
        last_answer=values["last_answer"]
    )

@router.post("/{id}/answers", response_model=SubmitAnswerResponse)
async def submit_answers(request:AnswerSubmitSchema, id: str):
    config = {"configurable": {"thread_id": id}}
    current_state = compiled_graph.get_state(config)
    if not current_state or not current_state.values:
        raise HTTPException(status_code=404, detail="Session not found")




    values = current_state.values
    idx = values.get("current_question_idx", 0)
    
    if idx >= 5:
        raise HTTPException(status_code=400, detail="All questions already answered")

    question = values["data"][idx]["question"]

    # Create state with the answer
    eval_state = {
        **values,
        "last_answer": request.answer.strip()
    }
    
    # Call evaluate_answer node function directly
    updated_state = evaluate_answer(eval_state)
    
    # Update the graph state
    compiled_graph.update_state(config, updated_state)
    
    # Prepare response
    feedback = updated_state["data"][idx]["feedback"]
    next_q_idx = None
    next_q = None
    updated_idx = None
    if updated_state.get("current_question_idx", 0) < 5:
        next_q_idx = updated_state["current_question_idx"]
        next_q = updated_state["data"][next_q_idx]["question"]
        updated_idx = updated_state["current_question_idx"]


    questions = [row["question"] for row in updated_state.get("data", [])]
    print(questions, "questions in submit answer")

    return SubmitAnswerResponse(
        id=id,
        current_question_idx=idx,
        question=question,
        feedback=feedback,
        next_question_idx=next_q_idx,
        next_question=next_q,
        questions = questions
    )


@router.get("/{id}/final_report")
def final_report(id: str):
    config = {"configurable": {"thread_id": id}}
    current_state = compiled_graph.get_state(config)

    # print(current_state.values)

    final_report = generate_final_report(current_state.values)
    current_state.values["final_report"] = final_report["final_report"]
    return {
        "id":id,
        "job_role":current_state.values["job_role"],
        "experience":current_state.values["experience"],
        "questions":current_state.values["data"],
        "current_question_idx":current_state.values["current_question_idx"],
        "final_report":current_state.values["final_report"]
    }


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using OpenAI's TTS API.
    Returns audio file in mp3 format.
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Generate speech using OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice=request.voice,
            input=request.text
        )
        
        # Return audio as streaming response
        audio_content = response.content
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")



@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    🎤 SPEECH-TO-TEXT ENDPOINT
    
    Convert speech to text using OpenAI's Whisper API.
    Accepts audio file and returns transcribed text.
    
    Request: Multipart form data with audio file
    
    Response example:
    {
        "text": "This is my answer to your question...",
        "language": "en",
        "duration": 5.2
    }
    """
    try:
        # ========================================
        # STEP A: Validate Audio File
        # ========================================
        if not audio.filename:
            raise HTTPException(
                status_code=400,
                detail="No audio file provided"
            )
        
        # Check file format (Whisper supports: mp3, mp4, mpeg, mpga, m4a, wav, webm)
        allowed_extensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        file_extension = os.path.splitext(audio.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {file_extension}. Supported: {', '.join(allowed_extensions)}"
            )
        
        # ========================================
        # STEP B: Read Audio Data
        # ========================================
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty"
            )
        
        # ========================================
        # STEP C: Connect to OpenAI
        # ========================================
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # ========================================
        # STEP D: Transcribe Audio
        # ========================================
        # Create file-like object for OpenAI
        audio_file = BytesIO(audio_data)
        audio_file.name = audio.filename
        
        # Call Whisper API
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            response_format="verbose_json"
        )
        
        # ========================================
        # STEP E: Return Transcription
        # ========================================
        return {
            "text": transcript.text,
            "language": transcript.language,
            "duration": transcript.duration
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
        
    except Exception as e:
        # Log error for debugging
        print(f"STT Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"STT Error: {str(e)}"
        )
    
    finally:
        # Cleanup - close the uploaded file
        await audio.close()