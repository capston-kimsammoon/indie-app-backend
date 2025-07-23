# app/scripts/insert_venues.py

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.venue import Venue
from app.scripts.venue_data import venue_data  # 경로 주의: scripts 내부에 있을 경우

def insert_venues():
    session: Session = SessionLocal()
    try:
        for data in venue_data:
            venue = Venue(**data)
            session.add(venue)
        session.commit()
        print("✅ 공연장 데이터 삽입 완료")
    except Exception as e:
        session.rollback()
        print(f"❌ 에러 발생: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    insert_venues()
