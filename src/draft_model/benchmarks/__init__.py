from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class BenchmarkSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    publisher_shape: str
    published_at: date
    player_id: str
    rank: int
    synthetic: bool

    def assert_eligible(self, as_of: date) -> None:
        if self.published_at > as_of:
            raise ValueError("benchmark snapshot was published after the prediction cutoff")
        if not self.synthetic:
            raise ValueError("phase-1 benchmark snapshots must be synthetic")
