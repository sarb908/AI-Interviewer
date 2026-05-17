from fastapi import APIRouter
from uuid import UUID, uuid1
from schema.session import SessionBase, SessionDisplay



router = APIRouter(prefix="/session", tags=["session"])

sessions:dict[str, SessionDisplay] = {}

@router.post("/", response_model=SessionDisplay)
def create_session(request: SessionBase):
    id = str(uuid1())  # Generate a dummy UUID for demonstration
    session_display = SessionDisplay(id=id, job_role=request.job_role, experience=request.experience)
    sessions[id] = session_display
    return session_display  


