from pprint import pprint

from analysis.estimators import cross_sectional_std, summarize_terminal_costs
from Config import (
    DAILY_STEPS,
    DEFAULT_RANDOM_SEED,
    K,
    MU,
    N_SHARES,
    PROJECT_NAME,
    R,
    S0,
    SIGMA,
    T,
    WEEKLY_STEPS,
)
from core.bsm import call_delta, call_price, d1, d2
from core.gbm import simulate_multiple_gbm_paths, simulate_single_gbm_path, summarize_terminal_prices
from core.grids import build_time_grid, build_time_to_maturity_grid, step_size
from core.hedge_engine import compact_hedge_table, run_multiple_path_delta_hedge, run_single_path_delta_hedge
from core.payoff import european_call_payoff, is_in_the_money



def build_stage1_summary() -> dict:
    price_per_share = call_price(S=S0, K=K, r=R, sigma=SIGMA, tau=T)
    delta_at_0 = call_delta(S=S0, K=K, r=R, sigma=SIGMA, tau=T)
    option_value_total = price_per_share * N_SHARES

    weekly_time_grid = build_time_grid(WEEKLY_STEPS)
    daily_time_grid = build_time_grid(DAILY_STEPS)

    summary = {
        "project_name": PROJECT_NAME,
        "inputs": {
            "S0": S0,
            "K": K,
            "T": T,
            "r": R,
            "sigma": SIGMA,
            "n_shares": N_SHARES,
        },
        "bsm": {
            "d1": d1(S0, K, R, SIGMA, T),
            "d2": d2(S0, K, R, SIGMA, T),
            "call_price_per_share": price_per_share,
            "call_delta_at_time_0": delta_at_0,
            "call_price_total_position": option_value_total,
        },
        "payoff_examples": {
            "payoff_if_ST_48": european_call_payoff(48.0, K),
            "payoff_if_ST_55": european_call_payoff(55.0, K),
            "itm_if_ST_48": is_in_the_money(48.0, K),
            "itm_if_ST_55": is_in_the_money(55.0, K),
        },
        "grids": {
            "weekly_n_steps": WEEKLY_STEPS,
            "weekly_dt": step_size(WEEKLY_STEPS),
            "weekly_first_five_t": weekly_time_grid[:5],
            "weekly_first_five_tau": build_time_to_maturity_grid(WEEKLY_STEPS)[:5],
            "daily_n_steps": DAILY_STEPS,
            "daily_dt": step_size(DAILY_STEPS),
            "daily_first_five_t": daily_time_grid[:5],
            "daily_first_five_tau": build_time_to_maturity_grid(DAILY_STEPS)[:5],
        },
    }
    return summary



def build_stage2_summary() -> dict:
    weekly_single = simulate_single_gbm_path(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=WEEKLY_STEPS,
        seed=DEFAULT_RANDOM_SEED,
    )
    daily_single = simulate_single_gbm_path(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=DAILY_STEPS,
        seed=DEFAULT_RANDOM_SEED,
    )

    weekly_many = simulate_multiple_gbm_paths(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=WEEKLY_STEPS,
        n_paths=5,
        seed=DEFAULT_RANDOM_SEED,
    )
    daily_many = simulate_multiple_gbm_paths(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=DAILY_STEPS,
        n_paths=5,
        seed=DEFAULT_RANDOM_SEED,
    )

    summary = {
        "stage": 2,
        "gbm_model": {
            "S0": S0,
            "mu": MU,
            "sigma": SIGMA,
            "T": T,
        },
        "weekly_single_path": {
            "n_steps": WEEKLY_STEPS,
            "first_five_prices": weekly_single["prices"][:5],
            "last_five_prices": weekly_single["prices"][-5:],
            "first_five_shocks": weekly_single["shocks"][:5],
            "terminal_price": weekly_single["prices"][-1],
        },
        "daily_single_path": {
            "n_steps": DAILY_STEPS,
            "first_five_prices": daily_single["prices"][:5],
            "last_five_prices": daily_single["prices"][-5:],
            "first_five_shocks": daily_single["shocks"][:5],
            "terminal_price": daily_single["prices"][-1],
        },
        "weekly_path_summary_5_paths": summarize_terminal_prices(weekly_many),
        "daily_path_summary_5_paths": summarize_terminal_prices(daily_many),
    }
    return summary



def build_stage3_summary() -> dict:
    weekly_single = simulate_single_gbm_path(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=WEEKLY_STEPS,
        seed=DEFAULT_RANDOM_SEED,
    )
    daily_single = simulate_single_gbm_path(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=DAILY_STEPS,
        seed=DEFAULT_RANDOM_SEED,
    )

    weekly_hedge = run_single_path_delta_hedge(weekly_single["prices"], WEEKLY_STEPS)
    daily_hedge = run_single_path_delta_hedge(daily_single["prices"], DAILY_STEPS)

    return {
        "stage": 3,
        "weekly_single_path_hedge": compact_hedge_table(weekly_hedge),
        "daily_single_path_hedge": compact_hedge_table(daily_hedge),
    }



def build_stage4_summary() -> dict:
    weekly_paths = simulate_multiple_gbm_paths(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=WEEKLY_STEPS,
        n_paths=10,
        seed=DEFAULT_RANDOM_SEED,
    )
    daily_paths = simulate_multiple_gbm_paths(
        S0=S0,
        mu=MU,
        sigma=SIGMA,
        maturity=T,
        n_steps=DAILY_STEPS,
        n_paths=10,
        seed=DEFAULT_RANDOM_SEED,
    )

    weekly_multi = run_multiple_path_delta_hedge(weekly_paths, WEEKLY_STEPS)
    daily_multi = run_multiple_path_delta_hedge(daily_paths, DAILY_STEPS)

    weekly_std_xt = cross_sectional_std(weekly_multi["cumulative_cost_paths"])
    daily_std_xt = cross_sectional_std(daily_multi["cumulative_cost_paths"])

    return {
        "stage": 4,
        "weekly_multi_path_summary": summarize_terminal_costs(
            weekly_multi["terminal_costs"], weekly_multi["itm_flags"]
        ),
        "daily_multi_path_summary": summarize_terminal_costs(
            daily_multi["terminal_costs"], daily_multi["itm_flags"]
        ),
        "weekly_std_X_t_first_five": weekly_std_xt[:5],
        "weekly_std_X_t_last_five": weekly_std_xt[-5:],
        "daily_std_X_t_first_five": daily_std_xt[:5],
        "daily_std_X_t_last_five": daily_std_xt[-5:],
        "weekly_first_two_terminal_X_T": weekly_multi["terminal_costs"][:2],
        "daily_first_two_terminal_X_T": daily_multi["terminal_costs"][:2],
    }



def main(stage: int = 1) -> None:
    if stage == 1:
        print("STAGE 1 CHECK")
        pprint(build_stage1_summary())
        return

    if stage == 2:
        print("STAGE 1 FOUNDATION")
        pprint(build_stage1_summary())
        print("\nSTAGE 2 CHECK")
        pprint(build_stage2_summary())
        return

    if stage == 3:
        print("STAGE 1 FOUNDATION")
        pprint(build_stage1_summary())
        print("\nSTAGE 2 FOUNDATION")
        pprint(build_stage2_summary())
        print("\nSTAGE 3 CHECK")
        pprint(build_stage3_summary())
        return

    if stage == 4:
        print("STAGE 4 CHECK")
        pprint(build_stage4_summary())
        return

    raise ValueError("Only stage 1, stage 2, stage 3, and stage 4 are currently implemented")


if __name__ == "__main__":
    main(stage=4)
