from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from models import Review, ReviewCreate, ReviewRead
from database import get_session

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead, status_code=201)
def create_review(
    review: ReviewCreate, session: Session = Depends(get_session)
) -> ReviewRead:

    db_review = Review(**review.model_dump())

    try:
        session.add(db_review)
        session.commit()
        session.refresh(db_review)

        return db_review

    except Exception:
        session.rollback()
        raise


@router.get("/", response_model=list[ReviewRead])
def list_reviews(
    play_name: str | None = Query(None, description="Filter by play name"),
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=50, description="Max reviews to return"),
    session: Session = Depends(get_session),
):
    query = select(Review)

    if play_name:
        query = query.where(Review.play_name == play_name)

    query = query.offset(skip).limit(limit)
    reviews = session.exec(query).all()
    return reviews
