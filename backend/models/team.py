"""
SQLAlchemy model for Teams.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.competition import Competition
    from backend.models.player_stats import PlayerStat


class Team(Base):
    """
    Represents a cricket team (franchise or national).
    """
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(10))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    competition: Mapped[Optional["Competition"]] = relationship("Competition", back_populates="teams")
    player_stats: Mapped[List["PlayerStat"]] = relationship("PlayerStat", back_populates="team", lazy="select")

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', short_name='{self.short_name}')>"
