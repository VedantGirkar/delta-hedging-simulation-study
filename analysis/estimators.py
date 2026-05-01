import math
from typing import Dict, List



def sample_mean(values: List[float]) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    return sum(values) / len(values)



def sample_variance(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sample_mean(values)
    return sum((x - mean_value) ** 2 for x in values) / (len(values) - 1)



def sample_std(values: List[float]) -> float:
    return math.sqrt(sample_variance(values))



def proportion(values: List[int]) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    return sum(values) / len(values)



def cross_sectional_std(paths: List[List[float]]) -> List[float]:
    if not paths:
        raise ValueError("paths cannot be empty")
    n_times = len(paths[0])
    for path in paths:
        if len(path) != n_times:
            raise ValueError("all paths must have the same length")

    stds = []
    for t in range(n_times):
        values_at_t = [path[t] for path in paths]
        stds.append(sample_std(values_at_t))
    return stds



def summarize_terminal_costs(terminal_costs: List[float], itm_flags: List[int]) -> Dict[str, float]:
    return {
        "n_paths": len(terminal_costs),
        "mean_X_T": sample_mean(terminal_costs),
        "std_X_T": sample_std(terminal_costs),
        "variance_X_T": sample_variance(terminal_costs),
        "itm_probability_estimate": proportion(itm_flags),
        "min_X_T": min(terminal_costs),
        "max_X_T": max(terminal_costs),
    }
