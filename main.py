from fastapi import FastAPI
from schemas import ProblemResponse,ProblemCreate
app=FastAPI()

problems = [
    {"id": 1, "problem_name": "Two Sum", "tags": ["array", "hashing"]}
]

@app.get("/")
async def index():
    return "Welcome to my first-Fastapi blog"

@app.get("/api/problems",response_model=list[ProblemResponse])
def get_prob():
    return problems
