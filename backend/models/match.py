"""
SQLAlchemy model for Matches.
"""
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Date, DateTime, Text, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.competition import Competition
    from backend.models.team import Team
    from backend.models.delivery import Delivery
    from backend.models.player_stats import PlayerStat


class Match(Base):
    """
    Represents a single cricket match.
    """
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cricsheet_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"))
    season: Mapped[Optional[str]] = mapped_column(String(20))
    match_date: Mapped[Optional[date]] = mapped_column(Date)
    venue: Mapped[Optional[str]] = mapped_column(String(150))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    team1_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))
    team2_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))
    toss_winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))
    toss_decision: Mapped[Optional[str]] = mapped_column(String(10))
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))
    win_by_runs: Mapped[Optional[int]] = mapped_column(Integer)
    win_by_wickets: Mapped[Optional[int]] = mapped_column(Integer)
    player_of_match: Mapped[Optional[str]] = mapped_column(String(120))
    match_type: Mapped[Optional[str]] = mapped_column(String(20))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    json_source: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("toss_decision IN ('bat', 'field')", name="ck_match_toss_decision"),
        Index("idx_matches_competition", "competition_id"),
        Index("idx_matches_season", "season"),
        Index("idx_matches_date", "match_date"),
    )

    # Relationships
    competition: Mapped[Optional["Competition"]] = relationship("Competition", back_populates="matches")
    team1: Mapped[Optional["Team"]] = relationship("Team", foreign_keys=[team1_id])
    team2: Mapped[Optional["Team"]] = relationship("Team", foreign_keys=[team2_id])
    toss_winner: Mapped[Optional["Team"]] = relationship("Team", foreign_keys=[toss_winner_id])
    winner: Mapped[Optional["Team"]] = relationship("Team", foreign_keys=[winner_id])
    deliveries: Mapped[List["Delivery"]] = relationship("Delivery", back_populates="match",
                                                         cascade="all, delete-orphan", lazy="select")
    player_stats: Mapped[List["PlayerStat"]] = relationship("PlayerStat", back_populates="match",
                                                              cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Match(id={self.id}, cricsheet_id='{self.cricsheet_id}')>"
