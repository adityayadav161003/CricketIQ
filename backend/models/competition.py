"""
SQLAlchemy model for Competitions.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Competition(Base):
    """
    Represents a cricket league or tournament (e.g., IPL, T20I).
    """
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("gender IN ('male', 'female', 'mixed')", name="ck_competition_gender"),
    )

    # Relationships
    teams: Mapped[List["Team"]] = relationship("Team", back_populates="competition", lazy="select")
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="competition", lazy="select")
    player_stats: Mapped[List["PlayerStat"]] = relationship("PlayerStat", back_populates="competition", lazy="select")

    def __repr__(self) -> str:
        return f"<Competition(id={self.id}, code='{self.code}', name='{self.name}')>"
