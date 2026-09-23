from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func

from models import Review, ReviewCreate, ReviewRead, ReviewUpdate, AverageRatingResponse
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


@router.get(
    "/average/{play_name}",
    response_model=AverageRatingResponse,
    summary="Get average rating",
    description="Get the average rating and total number of reviews for a play."
)
def get_average_rating(
    play_name: str,
    session: Session = Depends(get_session)
):
    query = select(
        func.avg(Review.rating),
        func.count(Review.id)
    ).where(
        Review.play_name == play_name
    )

    result = session.exec(query).first()

    avg_rating, total_reviews = result

    if total_reviews == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No reviews found for {play_name}"
        )

    return AverageRatingResponse(
        play_name=play_name,
        average_rating=round(float(avg_rating), 2),
        total_reviews=total_reviews
    )
    
    
@router.get("/{review_id}",response_model=ReviewRead)
def get_review(
    review_id:int,
    session: Session = Depends(get_session)
):
    review = session.get(Review,review_id)
    if not review:
        raise HTTPException(status_code=404,detail=f"No review found for this review id:{review_id}")
    
    return review



@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    status_code=status.HTTP_200_OK,
    summary="Update a review",
    description="Update one or more fields of an existing review."
)
def update_review(
    review_id: int,
    update: ReviewUpdate,
    session: Session = Depends(get_session)
):
    # Find the existing review
    review = session.get(Review, review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No review found with id: {review_id}"
        )

    # Get only fields provided by the client
    update_data = update.model_dump(exclude_unset=True)

    # Apply the updates to the existing review
    for field, value in update_data.items():
        setattr(review, field, value)

    try:
        session.add(review)
        session.commit()
        session.refresh(review)

    except Exception:
        session.rollback()
        raise

    return review
    



@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a review",
    description="Delete an existing review by its ID."
)
def delete_review(
    review_id: int,
    session: Session = Depends(get_session)
):
    # Find the review
    review = session.get(Review, review_id)

    # Review not found
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No review found with id: {review_id}"
        )

    try:
        # Delete the review
        session.delete(review)
        session.commit()

    except Exception:
        # Rollback if database operation fails
        session.rollback()
        raise

    return {
        "message": "Review deleted successfully",
        "review_id": review_id
    }
