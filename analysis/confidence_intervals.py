import math
from typing import Dict, List

from Config import CONFIDENCE_LEVEL
from analysis.estimators import proportion, sample_mean, sample_std


Z_95 = 1.96



def mean_confidence_interval(values: List[float], confidence_level: float = CONFIDENCE_LEVEL) -> Dict[str, float]:
    if not values:
        raise ValueError("values cannot be empty")
    n = len(values)
    mean_value = sample_mean(values)
    std_value = sample_std(values)
    z = Z_95 if abs(confidence_level - 0.95) < 1e-12 else Z_95
    half_width = z * std_value / math.sqrt(n) if n > 0 else 0.0
    return {
        "confidence_level": confidence_level,
        "mean": mean_value,
        "std": std_value,
        "n": n,
        "half_width": half_width,
        "lower": mean_value - half_width,
        "upper": mean_value + half_width,
        "relative_half_width": abs(half_width / mean_value) if mean_value != 0 else math.inf,
    }



def proportion_confidence_interval(flags: List[int], confidence_level: float = CONFIDENCE_LEVEL) -> Dict[str, float]:
    if not flags:
        raise ValueError("flags cannot be empty")
    n = len(flags)
    p_hat = proportion(flags)
    z = Z_95 if abs(confidence_level - 0.95) < 1e-12 else Z_95
    half_width = z * math.sqrt(max(p_hat * (1.0 - p_hat), 0.0) / n)
    lower = max(0.0, p_hat - half_width)
    upper = min(1.0, p_hat + half_width)
    return {
        "confidence_level": confidence_level,
        "n": n,
        "p_hat": p_hat,
        "half_width": half_width,
        "lower": lower,
        "upper": upper,
    }



def interval_covers_value(lower: float, upper: float, benchmark: float) -> bool:
    return lower <= benchmark <= upper
