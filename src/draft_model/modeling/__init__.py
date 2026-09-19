from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from draft_model.contracts import DataMode, FeatureRow, Prediction, Role, label_for_data_mode


@dataclass(frozen=True)
class FittedModel:
    role: Role
    mean: np.ndarray
    scale: np.ndarray
    coefficients: np.ndarray
    residual_scale: float


def fit(rows: list[FeatureRow], role: Role) -> FittedModel:
    selected = [r for r in rows if r.role == role and r.outcome_war is not None]
    if len(selected) < 4:
        raise ValueError(f"at least four training rows required for {role}")
    matrix = np.asarray([r.values for r in selected], dtype=float)
    target = np.asarray([r.outcome_war for r in selected], dtype=float)
    mean = matrix.mean(axis=0)
    scale = matrix.std(axis=0)
    scale[scale < 1e-9] = 1.0
    standardized = (matrix - mean) / scale
    design = np.column_stack([np.ones(len(standardized)), standardized])
    penalty = np.eye(design.shape[1]) * 1.0
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(design.T @ design + penalty, design.T @ target)
    residuals = target - design @ coefficients
    residual_scale = max(float(np.sqrt(np.mean(residuals**2))), 0.35)
    return FittedModel(role, mean, scale, coefficients, residual_scale)


def predict(model: FittedModel, row: FeatureRow, data_mode: DataMode = DataMode.DEMO) -> Prediction:
    vector = (np.asarray(row.values, dtype=float) - model.mean) / model.scale
    point = float(np.concatenate([[1.0], vector]) @ model.coefficients)
    sparsity = 1.0 + 0.30 / math.sqrt(row.observation_count)
    hs_multiplier = 1.65 if row.high_school else 1.0
    width = 1.96 * model.residual_scale * sparsity * hs_multiplier
    probability = 1.0 / (1.0 + math.exp(-(point - 2.0) / max(model.residual_scale, 0.5)))
    return Prediction(
        data_mode=data_mode,
        label=label_for_data_mode(data_mode),
        player_id=row.player_id,
        name=row.name,
        role=row.role,
        draft_year=row.draft_year,
        projected_war=round(point, 4),
        lower_war=round(point - width, 4),
        upper_war=round(point + width, 4),
        probability_two_war=round(probability, 4),
        uncertainty_width=round(width * 2, 4),
    )
