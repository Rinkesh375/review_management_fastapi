from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_tables
from routes.reviews import router as review_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan started.")
    create_tables()
    print("Database tables created")
    yield
    # shutdown: cleanup here
    print("Shutting down the app")

app = FastAPI(
    title="Review System API",
    description="API for managing and reviewing theatre performances, including user reviews, ratings, and feedback.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(review_router)