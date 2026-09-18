import datetime
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, UserReferralDB

class ReferralService:
    """
    Consumer Growth & Referral Engine.
    """

    @staticmethod
    async def create_referral(referrer_id: str, email: str) -> bool:
        with SessionLocal() as session:
            # Check if email already exists
            existing = session.query(UserReferralDB).filter(UserReferralDB.referred_email == email).first()
            if existing: return False

            ref = UserReferralDB(
                id=f"ref_{referrer_id[:4]}_{email.split('@')[0]}",
                referrer_id=referrer_id,
                referred_email=email,
                status="SENT"
            )
            session.add(ref)
            session.commit()
            return True

    @staticmethod
    async def process_conversion(referred_email: str):
        with SessionLocal() as session:
            ref = session.query(UserReferralDB).filter(UserReferralDB.referred_email == referred_email).first()
            if ref and ref.status == "SENT":
                ref.status = "CONVERTED"
                ref.reward_earned = 375.0 # 15% of PRO plan
                session.commit()
                print(f"[Referral] Reward granted to {ref.referrer_id} for {referred_email}")
