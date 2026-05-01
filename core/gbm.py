import math
import random
from typing import Dict, List, Optional

from Config import DEFAULT_RANDOM_SEED
from core.grids import step_size



def simulate_single_gbm_path(
    S0: float,
    mu: float,
    sigma: float,
    maturity: float,
    n_steps: int,
    seed: Optional[int] = None,
) -> Dict[str, List[float]]:
    if S0 <= 0:
        raise ValueError("S0 must be positive")
    if sigma < 0:
        raise ValueError("sigma cannot be negative")
    if n_steps <= 0:
        raise ValueError("n_steps must be positive")

    rng = random.Random(DEFAULT_RANDOM_SEED if seed is None else seed)
    dt = step_size(n_steps=n_steps, maturity=maturity)
    sqrt_dt = math.sqrt(dt)

    prices = [S0]
    shocks = []
    log_returns = []

    current_price = S0
    drift_term = (mu - 0.5 * sigma * sigma) * dt

    for _ in range(n_steps):
        z = rng.gauss(0.0, 1.0)
        diffusion_term = sigma * sqrt_dt * z
        gross_return = math.exp(drift_term + diffusion_term)
        next_price = current_price * gross_return

        shocks.append(z)
        log_returns.append(math.log(next_price / current_price))
        prices.append(next_price)
        current_price = next_price

    return {
        "prices": prices,
        "shocks": shocks,
        "log_returns": log_returns,
        "dt": [dt] * n_steps,
    }



def simulate_multiple_gbm_paths(
    S0: float,
    mu: float,
    sigma: float,
    maturity: float,
    n_steps: int,
    n_paths: int,
    seed: Optional[int] = None,
) -> List[List[float]]:
    if n_paths <= 0:
        raise ValueError("n_paths must be positive")

    base_seed = DEFAULT_RANDOM_SEED if seed is None else seed
    all_paths = []

    for i in range(n_paths):
        path_result = simulate_single_gbm_path(
            S0=S0,
            mu=mu,
            sigma=sigma,
            maturity=maturity,
            n_steps=n_steps,
            seed=base_seed + i,
        )
        all_paths.append(path_result["prices"])

    return all_paths



def summarize_terminal_prices(paths: List[List[float]]) -> Dict[str, float]:
    if not paths:
        raise ValueError("paths cannot be empty")

    terminal_prices = [path[-1] for path in paths]
    count = len(terminal_prices)
    mean_terminal = sum(terminal_prices) / count
    min_terminal = min(terminal_prices)
    max_terminal = max(terminal_prices)

    variance = 0.0
    if count > 1:
        variance = sum((x - mean_terminal) ** 2 for x in terminal_prices) / (count - 1)

    return {
        "n_paths": count,
        "mean_terminal_price": mean_terminal,
        "min_terminal_price": min_terminal,
        "max_terminal_price": max_terminal,
        "std_terminal_price": math.sqrt(variance),
    }
