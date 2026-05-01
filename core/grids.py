from typing import List

from Config import T



def build_time_grid(n_steps: int, maturity: float = T) -> List[float]:
    if n_steps <= 0:
        raise ValueError("n_steps must be positive")
    dt = maturity / n_steps
    return [i * dt for i in range(n_steps + 1)]



def build_time_to_maturity_grid(n_steps: int, maturity: float = T) -> List[float]:
    grid = build_time_grid(n_steps=n_steps, maturity=maturity)
    return [maturity - t for t in grid]



def step_size(n_steps: int, maturity: float = T) -> float:
    if n_steps <= 0:
        raise ValueError("n_steps must be positive")
    return maturity / n_steps
