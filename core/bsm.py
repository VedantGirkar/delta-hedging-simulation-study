import math

from Config import FLOAT_TOL


SQRT_TWO = math.sqrt(2.0)
SQRT_TWO_PI = math.sqrt(2.0 * math.pi)


def normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_TWO_PI



def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / SQRT_TWO))



def d1(S: float, K: float, r: float, sigma: float, tau: float) -> float:
    if tau <= FLOAT_TOL:
        raise ValueError("tau must be positive to compute d1")
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    numerator = math.log(S / K) + (r + 0.5 * sigma * sigma) * tau
    denominator = sigma * math.sqrt(tau)
    return numerator / denominator



def d2(S: float, K: float, r: float, sigma: float, tau: float) -> float:
    return d1(S, K, r, sigma, tau) - sigma * math.sqrt(tau)



def call_price(S: float, K: float, r: float, sigma: float, tau: float) -> float:
    if tau <= FLOAT_TOL:
        return max(S - K, 0.0)
    d1_val = d1(S, K, r, sigma, tau)
    d2_val = d2(S, K, r, sigma, tau)
    return S * normal_cdf(d1_val) - K * math.exp(-r * tau) * normal_cdf(d2_val)



def call_delta(S: float, K: float, r: float, sigma: float, tau: float) -> float:
    if tau <= FLOAT_TOL:
        if S > K:
            return 1.0
        if S < K:
            return 0.0
        return 0.5
    return normal_cdf(d1(S, K, r, sigma, tau))
