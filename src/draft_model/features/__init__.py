from __future__ import annotations

from datetime import date

from draft_model.contracts import FeatureRow, Prospect, Role, SourceKind


def _age_on(birth_date: date, as_of: date) -> float:
    return (as_of - birth_date).days / 365.2425


def build_features(prospect: Prospect, as_of: date) -> FeatureRow:
    future = [o for o in prospect.observations if o.available_at > as_of]
    if future:
        raise ValueError(f"post-cutoff observation for {prospect.player_id}")
    observations = prospect.observations
    if not observations:
        raise ValueError(f"no observations for {prospect.player_id}")

    total_weight = sum(1.5 if o.source_kind == SourceKind.SUMMER else 1.0 for o in observations)
    competition = sum(
        o.competition_strength * (1.5 if o.source_kind == SourceKind.SUMMER else 1.0)
        for o in observations
    ) / total_weight
    age_relative = _age_on(prospect.birth_date, as_of) - 20.5
    scouting = (prospect.tool_grade - 50.0) / 10.0
    summer_share = sum(o.source_kind == SourceKind.SUMMER for o in observations) / len(observations)
    # EADA program-resource context: public-domain federal data attached at
    # ingest with its own conservative publication cutoff, so any observation
    # carrying it was available at the observation date by construction.
    eada_values = [
        float(o.raw_fields["eada_budget_pct"])
        for o in observations
        if "eada_budget_pct" in o.raw_fields
    ]
    program_resources = sum(eada_values) / len(eada_values) if eada_values else 0.5

    if prospect.role == Role.HITTER:
        pa = sum(o.plate_appearances for o in observations)
        if pa <= 0:
            raise ValueError("hitter requires plate appearances")
        offense = sum(o.hits + o.walks + 3 * o.home_runs for o in observations) / pa
        discipline = 1.0 - sum(o.strikeouts for o in observations) / pa
        names = ["age_relative", "competition", "offense", "discipline", "scouting", "summer_share", "program_resources"]
        values = [age_relative, competition, offense, discipline, scouting, summer_share, program_resources]
    else:
        innings = sum(o.innings_pitched for o in observations)
        if innings <= 0:
            raise ValueError("pitcher requires innings")
        dominance = (sum(o.strikeouts for o in observations) - sum(o.walks for o in observations)) / innings
        strikes = sum((o.strike_percentage or 0.0) for o in observations) / len(observations)
        velocity = sum((o.fastball_velocity or 0.0) for o in observations) / len(observations)
        names = ["age_relative", "competition", "dominance", "strike_percentage", "velocity", "scouting", "program_resources"]
        values = [age_relative, competition, dominance, strikes, velocity, scouting, program_resources]

    return FeatureRow(
        player_id=prospect.player_id,
        name=prospect.name,
        role=prospect.role,
        draft_year=prospect.draft_year,
        values=values,
        feature_names=names,
        observation_count=len(observations),
        high_school=prospect.level == "high_school",
        outcome_war=prospect.outcome_war,
    )
