"""Savings calculators: compound growth, emergency funds, inflation-adjusted returns."""

import math


def compound_savings(
    monthly_deposit: float, annual_rate_pct: float, months: int, initial: float
) -> dict:
    """Project a savings balance with monthly deposits and monthly compounding.

    Deposits are made at the end of each month; interest compounds monthly at
    one twelfth of the annual rate.

    Args:
        monthly_deposit: Amount deposited each month, must be non-negative.
        annual_rate_pct: Annual interest rate in percent (e.g. 4 for 4%).
        months: Number of months to save, must be positive.
        initial: Starting balance, must be non-negative.

    Returns:
        Dict with keys "end_balance", "total_deposited" (initial plus all
        monthly deposits) and "total_interest" (end balance minus deposits).
        Money values are rounded to 2 decimals.
    """
    if monthly_deposit < 0:
        raise ValueError(f"monthly_deposit must be non-negative, got {monthly_deposit}")
    if annual_rate_pct < 0:
        raise ValueError(f"annual_rate_pct must be non-negative, got {annual_rate_pct}")
    if months <= 0:
        raise ValueError(f"months must be a positive integer, got {months}")
    if initial < 0:
        raise ValueError(f"initial must be non-negative, got {initial}")

    rate = annual_rate_pct / 100.0 / 12.0
    if rate == 0:
        end_balance = initial + monthly_deposit * months
    else:
        growth = (1 + rate) ** months
        end_balance = initial * growth + monthly_deposit * (growth - 1) / rate

    total_deposited = initial + monthly_deposit * months
    return {
        "end_balance": round(end_balance, 2),
        "total_deposited": round(total_deposited, 2),
        "total_interest": round(end_balance - total_deposited, 2),
    }


def emergency_fund_target(
    monthly_expenses: float,
    months_coverage: int,
    current_savings: float,
    monthly_contribution: float,
) -> dict:
    """Compute an emergency fund target and the time needed to reach it.

    Args:
        monthly_expenses: Average monthly living expenses, must be non-negative.
        months_coverage: Number of months the fund should cover, must be positive.
        current_savings: Amount already saved, must be non-negative.
        monthly_contribution: Amount added to the fund each month, must be
            non-negative.

    Returns:
        Dict with keys "target_amount" (expenses times coverage), "gap"
        (remaining amount to save, 0 if already reached) and "months_to_target"
        (whole months of contributions needed to close the gap; 0 if already
        reached, None if the gap is positive but the contribution is 0).
        Money values are rounded to 2 decimals.
    """
    if monthly_expenses < 0:
        raise ValueError(f"monthly_expenses must be non-negative, got {monthly_expenses}")
    if months_coverage <= 0:
        raise ValueError(f"months_coverage must be a positive integer, got {months_coverage}")
    if current_savings < 0:
        raise ValueError(f"current_savings must be non-negative, got {current_savings}")
    if monthly_contribution < 0:
        raise ValueError(
            f"monthly_contribution must be non-negative, got {monthly_contribution}"
        )

    target = monthly_expenses * months_coverage
    gap = max(0.0, target - current_savings)
    if gap == 0:
        months_to_target = 0
    elif monthly_contribution == 0:
        months_to_target = None
    else:
        months_to_target = math.ceil(gap / monthly_contribution)

    return {
        "target_amount": round(target, 2),
        "gap": round(gap, 2),
        "months_to_target": months_to_target,
    }


def real_return(nominal_rate_pct: float, inflation_rate_pct: float) -> dict:
    """Compute the inflation-adjusted (real) rate of return.

    Uses the Fisher equation (1 + real) = (1 + nominal) / (1 + inflation) for
    the exact rate, and the common approximation nominal minus inflation.

    Args:
        nominal_rate_pct: Nominal annual return in percent (e.g. 6 for 6%).
        inflation_rate_pct: Annual inflation rate in percent; must be greater
            than -100.

    Returns:
        Dict with keys "real_rate_exact_pct" (Fisher equation) and
        "real_rate_approx_pct" (nominal minus inflation), both in percent
        rounded to 4 decimals.
    """
    if inflation_rate_pct <= -100:
        raise ValueError(
            f"inflation_rate_pct must be greater than -100, got {inflation_rate_pct}"
        )

    nominal = nominal_rate_pct / 100.0
    inflation = inflation_rate_pct / 100.0
    exact = (1 + nominal) / (1 + inflation) - 1
    return {
        "real_rate_exact_pct": round(exact * 100, 4),
        "real_rate_approx_pct": round(nominal_rate_pct - inflation_rate_pct, 4),
    }
