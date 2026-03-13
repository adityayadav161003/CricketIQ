"""
SQLAlchemy model for ball-by-ball Deliveries.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, SmallInteger, String, Boolean, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.match import Match


class Delivery(Base):
    """
    Ball-by-ball delivery record. The core analytics table.
    """
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    innings: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    over: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ball: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    phase: Mapped[str] = mapped_column(String(10), nullable=False)     # powerplay | middle | death
    batter: Mapped[str] = mapped_column(String(120), nullable=False)
    non_striker: Mapped[Optional[str]] = mapped_column(String(120))
    bowler: Mapped[str] = mapped_column(String(120), nullable=False)
    runs_batter: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    runs_extras: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    runs_total: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    
    # Extras breakdown
    extras_wides: Mapped[int] = mapped_column(SmallInteger, default=0)
    extras_noballs: Mapped[int] = mapped_column(SmallInteger, default=0)
    extras_byes: Mapped[int] = mapped_column(SmallInteger, default=0)
    extras_legbyes: Mapped[int] = mapped_column(SmallInteger, default=0)
    extras_penalty: Mapped[int] = mapped_column(SmallInteger, default=0)
    
    # Dismissal
    is_wicket: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dismissal_type: Mapped[Optional[str]] = mapped_column(String(40))
    player_out: Mapped[Optional[str]] = mapped_column(String(120))
    fielder: Mapped[Optional[str]] = mapped_column(String(120))
    
    # Boundary and dot ball flags flags
    is_boundary_4: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_boundary_6: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_dot_ball: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("phase IN ('powerplay', 'middle', 'death')", name="ck_delivery_phase"),
        Index("idx_del_match", "match_id"),
        Index("idx_del_batter", "batter"),
        Index("idx_del_bowler", "bowler"),
        Index("idx_del_innings", "innings"),
        Index("idx_del_phase", "phase"),
        Index("idx_del_match_inn", "match_id", "innings"),
    )

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="deliveries")

    def __repr__(self) -> str:
        return (
            f"<Delivery(match_id={self.match_id}, innings={self.innings}, "
            f"over={self.over}, ball={self.ball}, batter='{self.batter}')>"
        )
