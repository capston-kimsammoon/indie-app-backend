# app/routers/review_report.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.review_report import ReviewReportCreate, ReviewReportResponse
from app.crud import review_report as report_crud
from app.models.user import User
from app.utils.dependency import get_current_user

router = APIRouter(prefix="/venue/review", tags=["ReviewReport"])

@router.post("/{review_id}/report", response_model=ReviewReportResponse, status_code=status.HTTP_201_CREATED)
def report_review(
    review_id: int,
    body: ReviewReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    from app.models.review import Review
    # 리뷰 존재 여부 확인
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    report = report_crud.create_review_report(db, review_id, user.id, body.reason)
    return report
