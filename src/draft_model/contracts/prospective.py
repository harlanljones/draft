from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from draft_model.contracts import SCHEMA_VERSION, DataMode, Role


class ProspectiveProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_package_id: str = Field(min_length=1)
    source_record_id: str = Field(min_length=1)
    observed_at: datetime
    available_at: datetime
    received_at: datetime
    collector: str = Field(min_length=1)
    method: str = Field(min_length=1)
    supersedes_record_id: str | None = None

    @field_validator("observed_at", "available_at", "received_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("prospective timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def timestamps_follow_evidence_flow(self) -> ProspectiveProvenance:
        if not self.observed_at <= self.available_at <= self.received_at:
            raise ValueError("timestamps must satisfy observed_at <= available_at <= received_at")
        return self


class ProspectivePlayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(pattern=r"^player_[a-z0-9_-]+$")
    display_name: str = Field(min_length=1)
    birth_date: date
    role: Role
    level: str = Field(min_length=1)
    bats: str | None = Field(default=None, pattern=r"^[LRS]$")
    throws: str | None = Field(default=None, pattern=r"^[LR]$")
    source_ids: dict[str, str] = Field(min_length=1)
    consent_version: str = Field(min_length=1)
    identified_public_release_allowed: bool


class ProspectiveRosterRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roster_record_id: str = Field(min_length=1)
    player_id: str
    organization_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    season: int = Field(ge=2026, le=2100)
    position: str = Field(min_length=1)
    eligibility_status: str = Field(min_length=1)
    provenance: ProspectiveProvenance


class ProspectiveGame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_id: str = Field(min_length=1)
    game_date: date
    home_team_id: str = Field(min_length=1)
    away_team_id: str = Field(min_length=1)
    competition_level: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    provenance: ProspectiveProvenance

    @model_validator(mode="after")
    def teams_must_differ(self) -> ProspectiveGame:
        if self.home_team_id == self.away_team_id:
            raise ValueError("home and away teams must differ")
        return self


class ProspectiveBattingLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    player_id: str
    game_id: str
    plate_appearances: int = Field(ge=0)
    at_bats: int = Field(ge=0)
    singles: int = Field(ge=0)
    doubles: int = Field(ge=0)
    triples: int = Field(ge=0)
    home_runs: int = Field(ge=0)
    walks: int = Field(ge=0)
    hit_by_pitch: int = Field(ge=0)
    strikeouts: int = Field(ge=0)
    sacrifice_flies: int = Field(ge=0)
    stolen_bases: int = Field(ge=0)
    caught_stealing: int = Field(ge=0)
    provenance: ProspectiveProvenance

    @model_validator(mode="after")
    def batting_components_are_possible(self) -> ProspectiveBattingLine:
        hits = self.singles + self.doubles + self.triples + self.home_runs
        if hits > self.at_bats:
            raise ValueError("hit components cannot exceed at_bats")
        if self.at_bats > self.plate_appearances:
            raise ValueError("at_bats cannot exceed plate_appearances")
        return self


class ProspectivePitchingLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1)
    player_id: str
    game_id: str
    outs_recorded: int = Field(ge=0)
    batters_faced: int = Field(ge=0)
    hits_allowed: int = Field(ge=0)
    runs: int = Field(ge=0)
    earned_runs: int = Field(ge=0)
    walks: int = Field(ge=0)
    hit_batters: int = Field(ge=0)
    strikeouts: int = Field(ge=0)
    home_runs_allowed: int = Field(ge=0)
    pitches: int | None = Field(default=None, ge=0)
    strikes: int | None = Field(default=None, ge=0)
    provenance: ProspectiveProvenance

    @model_validator(mode="after")
    def pitching_components_are_possible(self) -> ProspectivePitchingLine:
        if self.earned_runs > self.runs:
            raise ValueError("earned_runs cannot exceed runs")
        if self.strikes is not None and (self.pitches is None or self.strikes > self.pitches):
            raise ValueError("strikes require pitches and cannot exceed them")
        if self.outs_recorded > self.batters_faced * 3:
            raise ValueError("outs_recorded is inconsistent with batters_faced")
        return self


class ProspectiveMeasurement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    measurement_id: str = Field(min_length=1)
    player_id: str
    metric: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    device_make: str = Field(min_length=1)
    device_model: str = Field(min_length=1)
    hardware_version: str = Field(min_length=1)
    software_version: str = Field(min_length=1)
    calibration: str = Field(min_length=1)
    protocol: str = Field(min_length=1)
    attempt: int = Field(ge=1)
    operator: str = Field(min_length=1)
    environment: dict[str, Any]
    provenance: ProspectiveProvenance


class ProspectiveReleaseManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = SCHEMA_VERSION
    release_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    data_mode: DataMode
    cutoff: datetime
    source_package_ids: list[str] = Field(min_length=1)
    protocol_registration: str = Field(min_length=1)
    consent_version: str = Field(min_length=1)
    append_only: bool
    correction_log: str = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)

    @field_validator("cutoff")
    @classmethod
    def cutoff_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("release cutoff must include a timezone")
        return value

    @model_validator(mode="after")
    def release_must_preserve_evidence(self) -> ProspectiveReleaseManifest:
        if self.data_mode != DataMode.EMPIRICAL:
            raise ValueError("prospective releases must be explicitly empirical")
        if not self.append_only:
            raise ValueError("prospective releases must be append-only")
        if len(self.source_package_ids) != len(set(self.source_package_ids)):
            raise ValueError("source_package_ids must be unique")
        return self


PROSPECTIVE_SCHEMA_MODELS: tuple[type[BaseModel], ...] = (
    ProspectiveProvenance,
    ProspectivePlayer,
    ProspectiveRosterRecord,
    ProspectiveGame,
    ProspectiveBattingLine,
    ProspectivePitchingLine,
    ProspectiveMeasurement,
    ProspectiveReleaseManifest,
)
