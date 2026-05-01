from typing import Dict

from analysis.confidence_intervals import interval_covers_value, mean_confidence_interval, proportion_confidence_interval
from analysis.estimators import cross_sectional_std, summarize_terminal_costs
from Config import DEFAULT_RANDOM_SEED, MU, RELATIVE_ERROR_TOLERANCE, S0, SIGMA, T
from core.gbm import simulate_multiple_gbm_paths
from core.hedge_engine import run_multiple_path_delta_hedge



def run_precision_controlled_study(
    *,
    n_steps: int,
    benchmark_price_total: float,
    initial_n_paths: int = 25,
    batch_size: int = 25,
    max_n_paths: int = 300,
    seed: int = DEFAULT_RANDOM_SEED,
) -> Dict[str, object]:
    n_paths = initial_n_paths
    final_result = None

    while True:
        stock_paths = simulate_multiple_gbm_paths(
            S0=S0,
            mu=MU,
            sigma=SIGMA,
            maturity=T,
            n_steps=n_steps,
            n_paths=n_paths,
            seed=seed,
        )
        hedge_result = run_multiple_path_delta_hedge(stock_paths=stock_paths, n_steps=n_steps)
        summary = summarize_terminal_costs(hedge_result["terminal_costs"], hedge_result["itm_flags"])
        mean_ci = mean_confidence_interval(hedge_result["terminal_costs"])
        prob_ci = proportion_confidence_interval(hedge_result["itm_flags"])
        std_xt = cross_sectional_std(hedge_result["cumulative_cost_paths"])
        covers_bsm = interval_covers_value(mean_ci["lower"], mean_ci["upper"], benchmark_price_total)

        final_result = {
            "n_steps": n_steps,
            "n_paths": n_paths,
            "summary": summary,
            "mean_ci": mean_ci,
            "prob_ci": prob_ci,
            "std_X_t": std_xt,
            "covers_bsm_price": covers_bsm,
            "benchmark_price_total": benchmark_price_total,
            "relative_error_target": RELATIVE_ERROR_TOLERANCE,
            "target_met": mean_ci["relative_half_width"] <= RELATIVE_ERROR_TOLERANCE,
        }

        if final_result["target_met"] or n_paths >= max_n_paths:
            break
        n_paths += batch_size

    return final_result
