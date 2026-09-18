from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "1.0"
MODEL_VERSION = "demo-ridge-1.0"
DEMO_LABEL = "DEMO / NOT EMPIRICAL"


class Role(StrEnum):
    HITTER = "hitter"
    PITCHER = "pitcher"


class SourceKind(StrEnum):
    COLLEGE = "college"
    SUMMER = "summer"
    SHOWCASE = "showcase"


class DataMode(StrEnum):
    DEMO = "demo"
    EMPIRICAL = "empirical"


class SourceStatus(StrEnum):
    AVAILABLE = "available"
    CONDITIONAL = "conditional"
    UNAVAILABLE = "unavailable"
    UNRESOLVED = "unresolved"


class IdentityResolution(StrEnum):
    MATCHED_EXACT_ID = "matched_exact_id"
    MATCHED_NAME_DOB = "matched_name_dob"
    CONFLICT = "conflict"
    UNRESOLVED = "unresolved"


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    player_id: str
    source_kind: SourceKind
    source_name: str
    observed_on: date
    available_at: date
    synthetic: bool
    competition_strength: float = Field(ge=0.0, le=1.0)
    plate_appearances: int = Field(default=0, ge=0)
    hits: int = Field(default=0, ge=0)
    home_runs: int = Field(default=0, ge=0)
    walks: int = Field(default=0, ge=0)
    strikeouts: int = Field(default=0, ge=0)
    innings_pitched: float = Field(default=0.0, ge=0.0)
    strike_percentage: float | None = Field(default=None, ge=0.0, le=1.0)
    fastball_velocity: float | None = Field(default=None, ge=60.0, le=110.0)
    raw_fields: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def availability_follows_observation(self) -> Observation:
        if self.available_at < self.observed_on:
            raise ValueError("available_at cannot precede observed_on")
        return self


class Prospect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str
    name: str
    role: Role
    draft_year: int = Field(ge=2010, le=2100)
    birth_date: date
    level: str
    tool_grade: float = Field(ge=20.0, le=80.0)
    observations: list[Observation]
    outcome_war: float | None = None
    outcome_available_at: date | None = None


class FeatureRow(BaseModel):
    player_id: str
    name: str
    role: Role
    draft_year: int
    values: list[float]
    feature_names: list[str]
    observation_count: int
    high_school: bool
    outcome_war: float | None


class Prediction(BaseModel):
    schema_version: str = SCHEMA_VERSION
    model_version: str = MODEL_VERSION
    data_mode: DataMode = DataMode.DEMO
    label: str = DEMO_LABEL
    player_id: str
    name: str
    role: Role
    draft_year: int
    projected_war: float
    lower_war: float
    upper_war: float
    probability_two_war: float
    uncertainty_width: float


class BacktestFold(BaseModel):
    draft_year: int
    role: Role
    train_size: int
    test_size: int
    rank_correlation: float
    mean_absolute_error: float
    interval_coverage: float
    brier_score: float
    bust_flag_hit_rate: float
    benchmark_rank_correlation: float


class BacktestResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    model_version: str = MODEL_VERSION
    data_mode: DataMode = DataMode.DEMO
    label: str = DEMO_LABEL
    as_of: date
    folds: list[BacktestFold]
    limitations: list[str]


class BoardResponse(BaseModel):
    schema_version: str = SCHEMA_VERSION
    model_version: str = MODEL_VERSION
    data_mode: DataMode = DataMode.DEMO
    label: str = DEMO_LABEL
    as_of: date
    predictions: list[Prediction]
    limitations: list[str]


class RunManifest(BaseModel):
    schema_version: str = SCHEMA_VERSION
    model_version: str = MODEL_VERSION
    data_mode: DataMode = DataMode.DEMO
    label: str = DEMO_LABEL
    seed: int
    as_of: date
    input_checksum: str
    configuration: dict[str, Any]
    limitations: list[str]


class ReadinessGate(BaseModel):
    gate: str
    passed: bool
    evidence: str


class SourceDisposition(BaseModel):
    source: str
    status: SourceStatus
    permitted_role: str


class ReadinessResponse(BaseModel):
    schema_version: str = SCHEMA_VERSION
    status: str = "no_go"
    label: str = "EMPIRICAL DISABLED / NO-GO"
    evaluated_at: date
    gates: list[ReadinessGate]
    sources: list[SourceDisposition]
    decision_record: str


class SourcePackageFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bytes: int = Field(ge=0)
    media_type: str

    @field_validator("path")
    @classmethod
    def path_must_be_relative(cls, value: str) -> str:
        parts = value.replace("\\", "/").split("/")
        if not value or value.startswith(("/", "\\")) or ".." in parts or "." in parts:
            raise ValueError("source package paths must be normalized relative paths")
        return value


class RightsGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agreement_reference: str = Field(min_length=1)
    reviewed_by: str = Field(min_length=1)
    reviewed_at: date
    allows_retention: bool
    allows_model_training: bool
    allows_derived_publication: bool
    allows_public_predictions: bool
    allows_raw_redistribution: bool

    @model_validator(mode="after")
    def required_rights_are_granted(self) -> RightsGrant:
        required = {
            "retention": self.allows_retention,
            "model training": self.allows_model_training,
            "derived publication": self.allows_derived_publication,
            "public predictions": self.allows_public_predictions,
        }
        denied = [name for name, granted in required.items() if not granted]
        if denied:
            raise ValueError(f"source package lacks required rights: {', '.join(denied)}")
        return self


class SourcePackageManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = SCHEMA_VERSION
    package_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    source: str = Field(min_length=1)
    data_mode: DataMode
    retrieved_at: date
    source_available_at: date
    availability_evidence: str = Field(min_length=1)
    license_name: str = Field(min_length=1)
    license_url: str = Field(min_length=1)
    attribution: str = Field(min_length=1)
    rights: RightsGrant
    files: list[SourcePackageFile] = Field(min_length=1)

    @model_validator(mode="after")
    def empirical_package_is_coherent(self) -> SourcePackageManifest:
        if self.data_mode != DataMode.EMPIRICAL:
            raise ValueError("source packages are reserved for explicitly empirical inputs")
        if self.source_available_at > self.retrieved_at:
            raise ValueError("source_available_at cannot follow retrieved_at")
        paths = [item.path for item in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("source package file paths must be unique")
        return self


class PackageValidationResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    label: str = "EMPIRICAL PACKAGE VALIDATION ONLY / NOT MODEL READY"
    package_id: str
    source: str
    valid: bool
    files_verified: int
    total_bytes: int
    raw_redistribution_allowed: bool
    limitations: list[str]


class IdentityMatch(BaseModel):
    schema_version: str = SCHEMA_VERSION
    player_id: str
    register_package_id: str
    resolution: IdentityResolution
    matched_uuid: str | None
    candidate_uuids: list[str]
    method: str
    evidence: list[str]


class CohortYearAudit(BaseModel):
    draft_year: int
    total_players: int
    identity_resolved: int
    identity_conflicts: int
    identity_unresolved: int
    outcomes_resolved: int
    outcomes_unresolved: int
    outcomes_censored: int
    eligible_labels: int


class EmpiricalLabelAudit(BaseModel):
    schema_version: str = SCHEMA_VERSION
    label: str = "EMPIRICAL LABEL PREFLIGHT / NOT MODEL READY"
    status: str = "no_go"
    label_pipeline_complete: bool
    total_players: int
    eligible_labels: int
    eligible_rate: float
    identity_input_sha256: str
    outcome_input_sha256: str
    years: list[CohortYearAudit]
    limitations: list[str]
