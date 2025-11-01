# app/crud/review_report.py
from sqlalchemy.orm import Session
from app.models.review_report import ReviewReport

def create_review_report(db: Session, review_id: int, user_id: int, reason: str = None):
    report = ReviewReport(review_id=review_id, user_id=user_id, reason=reason)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_review_reports(db: Session, review_id: int):
    return db.query(ReviewReport).filter(ReviewReport.review_id == review_id).all()
