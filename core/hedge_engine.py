from typing import Dict, List

from Config import K, N_SHARES, R, SIGMA, T
from core.account import accrue_interest, settlement_cashflow, summarize_trade
from core.bsm import call_delta
from core.grids import build_time_grid, build_time_to_maturity_grid, step_size
from core.payoff import european_call_payoff, is_in_the_money



def run_single_path_delta_hedge(stock_prices: List[float], n_steps: int) -> Dict[str, object]:
    if len(stock_prices) != n_steps + 1:
        raise ValueError("stock_prices length must equal n_steps + 1")

    dt = step_size(n_steps=n_steps, maturity=T)
    times = build_time_grid(n_steps=n_steps, maturity=T)
    taus = build_time_to_maturity_grid(n_steps=n_steps, maturity=T)

    rows = []
    cumulative_cost = 0.0
    previous_shares_held = 0.0

    for i in range(n_steps + 1):
        current_stock_price = stock_prices[i]
        tau = taus[i]
        delta = call_delta(
            S=current_stock_price,
            K=K,
            r=R,
            sigma=SIGMA,
            tau=tau,
        )
        target_shares = delta * N_SHARES
        shares_purchased = target_shares - previous_shares_held

        interest_cost = 0.0 if i == 0 else accrue_interest(cumulative_cost, R, dt)
        trade_summary = summarize_trade(
            balance_before_trade=cumulative_cost,
            interest_cost=interest_cost,
            shares_trade=shares_purchased,
            stock_price=current_stock_price,
        )
        cumulative_cost = trade_summary["balance_after_trade"]

        rows.append(
            {
                "step": i,
                "time": times[i],
                "tau": tau,
                "stock_price": current_stock_price,
                "delta": delta,
                "target_shares": target_shares,
                "shares_purchased": shares_purchased,
                "trade_cost": trade_summary["trade_cost"],
                "interest_cost": trade_summary["interest_cost"],
                "cumulative_cost": cumulative_cost,
            }
        )
        previous_shares_held = target_shares

    final_stock_price = stock_prices[-1]
    option_payoff_per_share = european_call_payoff(final_stock_price, K)
    option_payoff_total = option_payoff_per_share * N_SHARES
    final_balance_after_settlement = settlement_cashflow(cumulative_cost, option_payoff_total)

    settlement = {
        "final_stock_price": final_stock_price,
        "option_payoff_per_share": option_payoff_per_share,
        "option_payoff_total": option_payoff_total,
        "itm_indicator": is_in_the_money(final_stock_price, K),
        "pre_settlement_balance": cumulative_cost,
        "terminal_X_T": final_balance_after_settlement,
    }

    return {
        "n_steps": n_steps,
        "dt": dt,
        "rows": rows,
        "settlement": settlement,
    }



def compact_hedge_table(hedge_result: Dict[str, object], first_n: int = 5, last_n: int = 3) -> Dict[str, object]:
    rows = hedge_result["rows"]
    if len(rows) <= first_n + last_n:
        sampled_rows = rows
    else:
        sampled_rows = rows[:first_n] + rows[-last_n:]

    return {
        "n_steps": hedge_result["n_steps"],
        "dt": hedge_result["dt"],
        "sampled_rows": sampled_rows,
        "settlement": hedge_result["settlement"],
    }
