from fastapi import FastAPI
from router.session import router as session_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="AI Interviewer Backend", version="0.1.0")
app.include_router(session_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ai-interviewer-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}