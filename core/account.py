from typing import Dict



def accrue_interest(balance: float, rate: float, dt: float) -> float:
    return balance * rate * dt



def apply_trade(balance: float, shares_trade: float, stock_price: float) -> float:
    trade_cost = shares_trade * stock_price
    return balance + trade_cost



def settlement_cashflow(final_balance: float, option_payoff_total: float) -> float:
    return final_balance - option_payoff_total



def summarize_trade(balance_before_trade: float, interest_cost: float, shares_trade: float, stock_price: float) -> Dict[str, float]:
    trade_cost = shares_trade * stock_price
    balance_after_interest = balance_before_trade + interest_cost
    balance_after_trade = balance_after_interest + trade_cost
    return {
        "balance_before_trade": balance_before_trade,
        "interest_cost": interest_cost,
        "balance_after_interest": balance_after_interest,
        "shares_trade": shares_trade,
        "trade_cost": trade_cost,
        "balance_after_trade": balance_after_trade,
    }
