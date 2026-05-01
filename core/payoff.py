def european_call_payoff(S_T: float, K: float) -> float:
    return max(S_T - K, 0.0)



def is_in_the_money(S_T: float, K: float) -> int:
    return int(S_T > K)
