"""
SQLAlchemy model for Players.
"""
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.player_stats import PlayerStat


class Player(Base):
    """
    Represents a unique cricket player profile.
    """
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cricsheet_key: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    batting_style: Mapped[Optional[str]] = mapped_column(String(30))
    bowling_style: Mapped[Optional[str]] = mapped_column(String(60))
    role: Mapped[Optional[str]] = mapped_column(String(30))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    stats: Mapped[List["PlayerStat"]] = relationship("PlayerStat", back_populates="player", lazy="select")

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}')>"
