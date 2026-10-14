from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from routers import problems,tags,patterns,attempts,auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(problems.router)
app.include_router(tags.router)
app.include_router(patterns.router)
app.include_router(attempts.router)
app.include_router(auth.router)

@app.get("/")
async def index():
    return "Welcome to my first-Fastapi blog"
