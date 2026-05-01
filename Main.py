from pathlib import Path
from pprint import pprint

from analysis.confidence_intervals import mean_confidence_interval, proportion_confidence_interval
from analysis.estimators import cross_sectional_std, summarize_terminal_costs
from analysis.precision_control import run_precision_controlled_study
from Config import (
    DAILY_STEPS, DEFAULT_RANDOM_SEED, K, MU, N_SHARES,
    PROJECT_NAME, R, RESULTS_DIR, S0, SIGMA, T, WEEKLY_STEPS,
)
from core.bsm import call_delta, call_price, d1, d2
from core.gbm import simulate_multiple_gbm_paths, simulate_single_gbm_path, summarize_terminal_prices
from core.grids import build_time_grid, build_time_to_maturity_grid, step_size
from core.hedge_engine import (
    compact_hedge_table, full_hedge_table_rows,
    run_multiple_path_delta_hedge, run_single_path_delta_hedge,
)
from core.payoff import european_call_payoff, is_in_the_money
from outputs.charts import (
    save_comparison_bar_chart, save_overlay_std_xt_plot,
    save_std_xt_plot, save_terminal_histogram,
)
from outputs.tables import write_dict_rows_to_csv
from outputs.dashboard_app import generate_dashboard


def build_stage1_summary() -> dict:
    price_per_share = call_price(S=S0, K=K, r=R, sigma=SIGMA, tau=T)
    delta_at_0 = call_delta(S=S0, K=K, r=R, sigma=SIGMA, tau=T)
    option_value_total = price_per_share * N_SHARES
    weekly_time_grid = build_time_grid(WEEKLY_STEPS)
    daily_time_grid = build_time_grid(DAILY_STEPS)
    return {
        "project_name": PROJECT_NAME,
        "inputs": {"S0": S0, "K": K, "T": T, "r": R, "sigma": SIGMA, "n_shares": N_SHARES},
        "bsm": {
            "d1": d1(S0, K, R, SIGMA, T), "d2": d2(S0, K, R, SIGMA, T),
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
            "weekly_n_steps": WEEKLY_STEPS, "weekly_dt": step_size(WEEKLY_STEPS),
            "weekly_first_five_t": weekly_time_grid[:5],
            "weekly_first_five_tau": build_time_to_maturity_grid(WEEKLY_STEPS)[:5],
            "daily_n_steps": DAILY_STEPS, "daily_dt": step_size(DAILY_STEPS),
            "daily_first_five_t": daily_time_grid[:5],
            "daily_first_five_tau": build_time_to_maturity_grid(DAILY_STEPS)[:5],
        },
    }


def build_stage2_summary() -> dict:
    weekly_single = simulate_single_gbm_path(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=WEEKLY_STEPS, seed=DEFAULT_RANDOM_SEED)
    daily_single  = simulate_single_gbm_path(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=DAILY_STEPS,  seed=DEFAULT_RANDOM_SEED)
    weekly_many   = simulate_multiple_gbm_paths(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=WEEKLY_STEPS, n_paths=5, seed=DEFAULT_RANDOM_SEED)
    daily_many    = simulate_multiple_gbm_paths(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=DAILY_STEPS,  n_paths=5, seed=DEFAULT_RANDOM_SEED)
    return {
        "stage": 2,
        "gbm_model": {"S0": S0, "mu": MU, "sigma": SIGMA, "T": T},
        "weekly_single_path": {
            "n_steps": WEEKLY_STEPS,
            "first_five_prices": weekly_single["prices"][:5],
            "last_five_prices":  weekly_single["prices"][-5:],
            "first_five_shocks": weekly_single["shocks"][:5],
            "terminal_price":    weekly_single["prices"][-1],
        },
        "daily_single_path": {
            "n_steps": DAILY_STEPS,
            "first_five_prices": daily_single["prices"][:5],
            "last_five_prices":  daily_single["prices"][-5:],
            "first_five_shocks": daily_single["shocks"][:5],
            "terminal_price":    daily_single["prices"][-1],
        },
        "weekly_path_summary_5_paths": summarize_terminal_prices(weekly_many),
        "daily_path_summary_5_paths":  summarize_terminal_prices(daily_many),
    }


def build_stage3_summary() -> dict:
    weekly_single = simulate_single_gbm_path(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=WEEKLY_STEPS, seed=DEFAULT_RANDOM_SEED)
    daily_single  = simulate_single_gbm_path(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=DAILY_STEPS,  seed=DEFAULT_RANDOM_SEED)
    weekly_hedge  = run_single_path_delta_hedge(weekly_single["prices"], WEEKLY_STEPS)
    daily_hedge   = run_single_path_delta_hedge(daily_single["prices"],  DAILY_STEPS)
    return {
        "stage": 3,
        "weekly_single_path_hedge": compact_hedge_table(weekly_hedge),
        "daily_single_path_hedge":  compact_hedge_table(daily_hedge),
    }


def build_stage4_summary() -> dict:
    weekly_paths = simulate_multiple_gbm_paths(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=WEEKLY_STEPS, n_paths=10, seed=DEFAULT_RANDOM_SEED)
    daily_paths  = simulate_multiple_gbm_paths(S0=S0, mu=MU, sigma=SIGMA, maturity=T, n_steps=DAILY_STEPS,  n_paths=10, seed=DEFAULT_RANDOM_SEED)
    weekly_multi = run_multiple_path_delta_hedge(weekly_paths, WEEKLY_STEPS)
    daily_multi  = run_multiple_path_delta_hedge(daily_paths,  DAILY_STEPS)
    weekly_std_xt = cross_sectional_std(weekly_multi["cumulative_cost_paths"])
    daily_std_xt  = cross_sectional_std(daily_multi["cumulative_cost_paths"])
    return {
        "stage": 4,
        "weekly_multi_path_summary": summarize_terminal_costs(weekly_multi["terminal_costs"], weekly_multi["itm_flags"]),
        "daily_multi_path_summary":  summarize_terminal_costs(daily_multi["terminal_costs"],  daily_multi["itm_flags"]),
        "weekly_std_X_t_first_five": weekly_std_xt[:5],
        "weekly_std_X_t_last_five":  weekly_std_xt[-5:],
        "daily_std_X_t_first_five":  daily_std_xt[:5],
        "daily_std_X_t_last_five":   daily_std_xt[-5:],
        "weekly_first_two_terminal_X_T": weekly_multi["terminal_costs"][:2],
        "daily_first_two_terminal_X_T":  daily_multi["terminal_costs"][:2],
    }


def build_stage5_summary() -> dict:
    benchmark_total_price = call_price(S=S0, K=K, r=R, sigma=SIGMA, tau=T) * N_SHARES
    weekly_study = run_precision_controlled_study(
        n_steps=WEEKLY_STEPS, benchmark_price_total=benchmark_total_price,
        initial_n_paths=25, batch_size=25, max_n_paths=200, seed=DEFAULT_RANDOM_SEED,
    )
    daily_study = run_precision_controlled_study(
        n_steps=DAILY_STEPS, benchmark_price_total=benchmark_total_price,
        initial_n_paths=25, batch_size=25, max_n_paths=200, seed=DEFAULT_RANDOM_SEED,
    )
    return {
        "stage": 5,
        "benchmark_total_bsm_price": benchmark_total_price,
        "weekly_precision_study": {
            "n_paths": weekly_study["n_paths"],
            "summary": weekly_study["summary"],
            "mean_ci": weekly_study["mean_ci"],
            "prob_ci": weekly_study["prob_ci"],
            "covers_bsm_price": weekly_study["covers_bsm_price"],
            "target_met": weekly_study["target_met"],
            "std_X_t_first_five": weekly_study["std_X_t"][:5],
        },
        "daily_precision_study": {
            "n_paths": daily_study["n_paths"],
            "summary": daily_study["summary"],
            "mean_ci": daily_study["mean_ci"],
            "prob_ci": daily_study["prob_ci"],
            "covers_bsm_price": daily_study["covers_bsm_price"],
            "target_met": daily_study["target_met"],
            "std_X_t_first_five": daily_study["std_X_t"][:5],
        },
    }


def build_stage6_summary() -> dict:
    benchmark_total_price = call_price(S=S0, K=K, r=R, sigma=SIGMA, tau=T) * N_SHARES

    weekly_study = run_precision_controlled_study(
        n_steps=WEEKLY_STEPS, benchmark_price_total=benchmark_total_price,
        initial_n_paths=25, batch_size=25, max_n_paths=200, seed=DEFAULT_RANDOM_SEED,
    )
    daily_study = run_precision_controlled_study(
        n_steps=DAILY_STEPS, benchmark_price_total=benchmark_total_price,
        initial_n_paths=25, batch_size=25, max_n_paths=200, seed=DEFAULT_RANDOM_SEED,
    )

    weekly_time = build_time_grid(WEEKLY_STEPS)
    daily_time  = build_time_grid(DAILY_STEPS)
    tables_dir  = RESULTS_DIR / "tables"
    figures_dir = RESULTS_DIR / "figures"

    summary_rows = [
        {
            "schedule": "weekly",
            "n_paths": weekly_study["n_paths"],
            "mean_X_T": weekly_study["summary"]["mean_X_T"],
            "std_X_T": weekly_study["summary"]["std_X_T"],
            "mean_ci_lower": weekly_study["mean_ci"]["lower"],
            "mean_ci_upper": weekly_study["mean_ci"]["upper"],
            "itm_probability": weekly_study["summary"]["itm_probability_estimate"],
            "prob_ci_lower": weekly_study["prob_ci"]["lower"],
            "prob_ci_upper": weekly_study["prob_ci"]["upper"],
            "covers_bsm_price": weekly_study["covers_bsm_price"],
            "target_met": weekly_study["target_met"],
        },
        {
            "schedule": "daily",
            "n_paths": daily_study["n_paths"],
            "mean_X_T": daily_study["summary"]["mean_X_T"],
            "std_X_T": daily_study["summary"]["std_X_T"],
            "mean_ci_lower": daily_study["mean_ci"]["lower"],
            "mean_ci_upper": daily_study["mean_ci"]["upper"],
            "itm_probability": daily_study["summary"]["itm_probability_estimate"],
            "prob_ci_lower": daily_study["prob_ci"]["lower"],
            "prob_ci_upper": daily_study["prob_ci"]["upper"],
            "covers_bsm_price": daily_study["covers_bsm_price"],
            "target_met": daily_study["target_met"],
        },
    ]
    write_dict_rows_to_csv(summary_rows, tables_dir / "weekly_daily_comparison.csv")

    # Save full per-path simulation tables (week/day, stock price, delta, shares, costs, X(T))
    all_path_rows = []
    for path_idx, result in enumerate(weekly_study["hedge_results"]):
        for row in full_hedge_table_rows(result):
            all_path_rows.append({"schedule": "weekly", "path": path_idx + 1, **row})
    for path_idx, result in enumerate(daily_study["hedge_results"]):
        for row in full_hedge_table_rows(result):
            all_path_rows.append({"schedule": "daily", "path": path_idx + 1, **row})
    write_dict_rows_to_csv(all_path_rows, tables_dir / "all_simulation_paths.csv")

    # Save terminal costs summary
    terminal_rows = []
    for i, (xt, itm) in enumerate(zip(weekly_study["terminal_costs"], weekly_study["itm_flags"])):
        terminal_rows.append({"schedule": "weekly", "path": i + 1, "X_T": round(xt, 4), "ITM": itm})
    for i, (xt, itm) in enumerate(zip(daily_study["terminal_costs"], daily_study["itm_flags"])):
        terminal_rows.append({"schedule": "daily", "path": i + 1, "X_T": round(xt, 4), "ITM": itm})
    write_dict_rows_to_csv(terminal_rows, tables_dir / "all_terminal_costs.csv")

    std_rows = []
    for t, w_std in zip(weekly_time, weekly_study["std_X_t"]):
        std_rows.append({"schedule": "weekly", "t": t, "std_X_t": w_std})
    for t, d_std in zip(daily_time, daily_study["std_X_t"]):
        std_rows.append({"schedule": "daily", "t": t, "std_X_t": d_std})
    write_dict_rows_to_csv(std_rows, tables_dir / "std_xt_paths.csv")

    save_std_xt_plot(weekly_time, weekly_study["std_X_t"], "Weekly rebalancing: Std of X(t)", figures_dir / "weekly_std_xt.png", "Weekly")
    save_std_xt_plot(daily_time,  daily_study["std_X_t"],  "Daily rebalancing: Std of X(t)",  figures_dir / "daily_std_xt.png",  "Daily")
    save_overlay_std_xt_plot(weekly_time, weekly_study["std_X_t"], daily_time, daily_study["std_X_t"], "Weekly vs Daily Std of X(t)", figures_dir / "weekly_daily_std_xt_overlay.png")
    save_terminal_histogram(weekly_study["terminal_costs"], "Weekly terminal X(T)", figures_dir / "weekly_terminal_xt_hist.png", "steelblue")
    save_terminal_histogram(daily_study["terminal_costs"],  "Daily terminal X(T)",  figures_dir / "daily_terminal_xt_hist.png",  "darkorange")
    save_comparison_bar_chart(["Weekly", "Daily"], [weekly_study["summary"]["mean_X_T"], daily_study["summary"]["mean_X_T"]], "Mean terminal X(T)", "Mean X(T)", figures_dir / "mean_xt_comparison.png")
    save_comparison_bar_chart(["Weekly", "Daily"], [weekly_study["summary"]["std_X_T"],  daily_study["summary"]["std_X_T"]],  "Std of terminal X(T)", "Std X(T)", figures_dir / "std_xt_terminal_comparison.png")

    return {
        "stage": 6,
        "benchmark_total_bsm_price": benchmark_total_price,
        "comparison_table_file": str(tables_dir / "weekly_daily_comparison.csv"),
        "all_simulation_paths_file": str(tables_dir / "all_simulation_paths.csv"),
        "all_terminal_costs_file": str(tables_dir / "all_terminal_costs.csv"),
        "std_xt_table_file": str(tables_dir / "std_xt_paths.csv"),
        "generated_figures": [
            str(figures_dir / "weekly_std_xt.png"),
            str(figures_dir / "daily_std_xt.png"),
            str(figures_dir / "weekly_daily_std_xt_overlay.png"),
            str(figures_dir / "weekly_terminal_xt_hist.png"),
            str(figures_dir / "daily_terminal_xt_hist.png"),
            str(figures_dir / "mean_xt_comparison.png"),
            str(figures_dir / "std_xt_terminal_comparison.png"),
        ],
        "weekly_summary": summary_rows[0],
        "daily_summary": summary_rows[1],
    }


def build_stage7_summary() -> dict:
    stage6 = build_stage6_summary()
    dashboard_dir  = RESULTS_DIR / "dashboard"
    dashboard_file = dashboard_dir / "delta_hedging_dashboard.html"
    generated_path = generate_dashboard(RESULTS_DIR, dashboard_file)
    return {
        "stage": 7,
        "dashboard_file": str(generated_path),
        "source_comparison_table": stage6["comparison_table_file"],
        "source_std_xt_table": stage6["std_xt_table_file"],
        "figure_count": len(stage6["generated_figures"]),
    }


def build_stage9_summary() -> dict:
    from report.exporter import build_submission_package
    final_package = build_submission_package()
    return {
        "stage": 9,
        "submission_dir": str(final_package["submission_dir"]),
        "report_file": str(final_package["report_file"]),
        "summary_file": str(final_package["summary_file"]),
        "appendix_dir": str(final_package["appendix_dir"]),
        "copied_file_count": final_package["copied_file_count"],
    }


def main(stage: int = 1) -> None:
    if stage == 1:
        print("STAGE 1 CHECK"); pprint(build_stage1_summary()); return
    if stage == 2:
        print("STAGE 2 CHECK"); pprint(build_stage2_summary()); return
    if stage == 3:
        print("STAGE 3 CHECK"); pprint(build_stage3_summary()); return
    if stage == 4:
        print("STAGE 4 CHECK"); pprint(build_stage4_summary()); return
    if stage == 5:
        print("STAGE 5 CHECK"); pprint(build_stage5_summary()); return
    if stage == 6:
        print("STAGE 6 CHECK"); pprint(build_stage6_summary()); return
    if stage == 7:
        print("STAGE 7 CHECK"); pprint(build_stage7_summary()); return
    if stage == 9:
        print("STAGE 9 CHECK"); pprint(build_stage9_summary()); return
    raise ValueError("Only stage 1 through stage 9 are currently implemented")


if __name__ == "__main__":
    main(stage=9)