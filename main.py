from fastapi import FastAPI
from schemas import ProblemResponse,ProblemCreate
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown (nothing needed here for now)

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def index():
    return "Welcome to my first-Fastapi blog"

@app.get("/api/problems",response_model=list[ProblemResponse])
def get_prob():
    pass
