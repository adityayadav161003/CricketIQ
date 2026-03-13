"""
SQLAlchemy model for PlayerStats.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, SmallInteger, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.player import Player
    from backend.models.match import Match
    from backend.models.competition import Competition
    from backend.models.team import Team


class PlayerStat(Base):
    """
    Pre-aggregated per-match statistics for a player.
    """
    __tablename__ = "player_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id", ondelete="SET NULL"))
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"))
    
    # Batting
    batting_runs: Mapped[int] = mapped_column(SmallInteger, default=0)
    balls_faced: Mapped[int] = mapped_column(SmallInteger, default=0)
    batting_fours: Mapped[int] = mapped_column(SmallInteger, default=0)
    batting_sixes: Mapped[int] = mapped_column(SmallInteger, default=0)
    batting_dots: Mapped[int] = mapped_column(SmallInteger, default=0)
    did_bat: Mapped[bool] = mapped_column(Boolean, default=False)
    was_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Bowling
    balls_bowled: Mapped[int] = mapped_column(SmallInteger, default=0)
    runs_conceded: Mapped[int] = mapped_column(SmallInteger, default=0)
    wickets: Mapped[int] = mapped_column(SmallInteger, default=0)
    bowling_dots: Mapped[int] = mapped_column(SmallInteger, default=0)
    bowling_fours: Mapped[int] = mapped_column(SmallInteger, default=0)
    bowling_sixes: Mapped[int] = mapped_column(SmallInteger, default=0)
    did_bowl: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Fantasy points
    fantasy_points: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("player_id", "match_id", name="uq_player_match"),
        Index("idx_pstats_player", "player_id"),
        Index("idx_pstats_match", "match_id"),
        Index("idx_pstats_comp", "competition_id"),
    )

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="stats")
    match: Mapped["Match"] = relationship("Match", back_populates="player_stats")
    competition: Mapped[Optional["Competition"]] = relationship("Competition", back_populates="player_stats")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="player_stats")

    def __repr__(self) -> str:
        return f"<PlayerStat(player_id={self.player_id}, match_id={self.match_id})>"
