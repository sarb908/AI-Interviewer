from fastapi import FastAPI
from router.session import router as session_router


app = FastAPI()
app.include_router(session_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}