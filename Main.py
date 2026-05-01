from pprint import pprint

from Config import DAILY_STEPS, K, N_SHARES, PROJECT_NAME, R, S0, SIGMA, T, WEEKLY_STEPS
from core.bsm import call_delta, call_price, d1, d2
from core.grids import build_time_grid, build_time_to_maturity_grid, step_size
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



def main() -> None:
    summary = build_stage1_summary()
    print("STAGE 1 CHECK")
    pprint(summary)


if __name__ == "__main__":
    main()
