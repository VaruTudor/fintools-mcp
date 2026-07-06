"""Mortgage calculators: payments, amortization, extra-payment payoff, refinancing."""

import math

AMORTIZATION_TYPES = ("annuity", "fixed_principal")


def _validate_loan(principal: float, annual_rate_pct: float, months: int) -> None:
    if principal < 0:
        raise ValueError(f"principal must be non-negative, got {principal}")
    if annual_rate_pct < 0:
        raise ValueError(f"annual_rate_pct must be non-negative, got {annual_rate_pct}")
    if months <= 0:
        raise ValueError(f"months must be a positive integer, got {months}")


def _validate_amortization(amortization: str) -> None:
    if amortization not in AMORTIZATION_TYPES:
        raise ValueError(
            f"amortization must be one of {AMORTIZATION_TYPES}, got {amortization!r}"
        )


def _monthly_rate(annual_rate_pct: float) -> float:
    return annual_rate_pct / 100.0 / 12.0


def _annuity_payment(principal: float, monthly_rate: float, months: int) -> float:
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def monthly_payment(
    principal: float, annual_rate_pct: float, months: int, amortization: str
) -> dict:
    """Compute the monthly payment for a mortgage.

    For an annuity loan the payment is constant. For a fixed-principal loan the
    principal part is constant and the interest part declines, so the first
    payment, last payment, and average payment are returned instead.

    Args:
        principal: Loan amount, must be non-negative.
        annual_rate_pct: Annual interest rate in percent (e.g. 6 for 6%).
        months: Loan term in months, must be positive.
        amortization: Repayment scheme, either "annuity" or "fixed_principal".

    Returns:
        For "annuity": dict with keys "amortization", "monthly_payment",
        "total_paid", "total_interest". For "fixed_principal": dict with keys
        "amortization", "first_payment", "last_payment", "average_payment",
        "total_paid", "total_interest". Money values are rounded to 2 decimals.
    """
    _validate_loan(principal, annual_rate_pct, months)
    _validate_amortization(amortization)
    rate = _monthly_rate(annual_rate_pct)

    if amortization == "annuity":
        payment = _annuity_payment(principal, rate, months)
        total_paid = payment * months
        return {
            "amortization": "annuity",
            "monthly_payment": round(payment, 2),
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_paid - principal, 2),
        }

    principal_part = principal / months
    first_payment = principal_part + principal * rate
    last_payment = principal_part + principal_part * rate
    total_interest = rate * principal * (months + 1) / 2
    total_paid = principal + total_interest
    return {
        "amortization": "fixed_principal",
        "first_payment": round(first_payment, 2),
        "last_payment": round(last_payment, 2),
        "average_payment": round(total_paid / months, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
    }


def amortization_schedule(
    principal: float, annual_rate_pct: float, months: int, amortization: str
) -> list[dict]:
    """Build a month-by-month amortization schedule for a mortgage.

    Args:
        principal: Loan amount, must be non-negative.
        annual_rate_pct: Annual interest rate in percent (e.g. 6 for 6%).
        months: Loan term in months, must be positive.
        amortization: Repayment scheme, either "annuity" or "fixed_principal".

    Returns:
        A list with one dict per month, each with keys "month" (1-based),
        "payment", "principal_part", "interest_part", "remaining_balance".
        Money values are rounded to 2 decimals.
    """
    _validate_loan(principal, annual_rate_pct, months)
    _validate_amortization(amortization)
    rate = _monthly_rate(annual_rate_pct)

    annuity = _annuity_payment(principal, rate, months) if amortization == "annuity" else 0.0
    fixed_part = principal / months

    schedule = []
    balance = principal
    for month in range(1, months + 1):
        interest_part = balance * rate
        if amortization == "annuity":
            principal_part = annuity - interest_part
        else:
            principal_part = fixed_part
        if month == months:
            principal_part = balance  # absorb float residue so the loan closes at 0
        payment = principal_part + interest_part
        balance -= principal_part
        schedule.append(
            {
                "month": month,
                "payment": round(payment, 2),
                "principal_part": round(principal_part, 2),
                "interest_part": round(interest_part, 2),
                "remaining_balance": round(balance, 2),
            }
        )
    return schedule


def _simulate_payoff(
    principal: float, rate: float, months: int, amortization: str, extra_monthly: float
) -> tuple[int, float]:
    """Simulate paying off a loan with an extra monthly amount.

    Returns:
        Tuple of (months until payoff, total interest paid). Not rounded.
    """
    annuity = _annuity_payment(principal, rate, months) if amortization == "annuity" else 0.0
    fixed_part = principal / months

    balance = principal
    total_interest = 0.0
    month = 0
    while balance > 1e-9 and month < months:
        month += 1
        interest = balance * rate
        total_interest += interest
        if amortization == "annuity":
            scheduled_principal = annuity - interest
        else:
            scheduled_principal = fixed_part
        principal_paid = min(balance, scheduled_principal + extra_monthly)
        balance -= principal_paid
    return month, total_interest


def payoff_simulation(
    principal: float,
    annual_rate_pct: float,
    months: int,
    amortization: str,
    extra_monthly: float,
) -> dict:
    """Simulate the effect of a constant extra monthly payment on a mortgage.

    Compares the baseline schedule with a schedule where extra_monthly is paid
    on top of every regular payment and applied directly to principal.

    Args:
        principal: Loan amount, must be non-negative.
        annual_rate_pct: Annual interest rate in percent (e.g. 6 for 6%).
        months: Original loan term in months, must be positive.
        amortization: Repayment scheme, either "annuity" or "fixed_principal".
        extra_monthly: Extra amount paid each month, must be non-negative.

    Returns:
        Dict with keys "months_saved" (int), "interest_saved",
        "new_payoff_months" (int, payoff date offset in months from now),
        "original_total_interest", "new_total_interest". Money values are
        rounded to 2 decimals.
    """
    _validate_loan(principal, annual_rate_pct, months)
    _validate_amortization(amortization)
    if extra_monthly < 0:
        raise ValueError(f"extra_monthly must be non-negative, got {extra_monthly}")
    rate = _monthly_rate(annual_rate_pct)

    base_months, base_interest = _simulate_payoff(principal, rate, months, amortization, 0.0)
    new_months, new_interest = _simulate_payoff(
        principal, rate, months, amortization, extra_monthly
    )
    return {
        "months_saved": base_months - new_months,
        "interest_saved": round(base_interest - new_interest, 2),
        "new_payoff_months": new_months,
        "original_total_interest": round(base_interest, 2),
        "new_total_interest": round(new_interest, 2),
    }


def refinance_breakeven(
    current_balance: float,
    current_rate_pct: float,
    new_rate_pct: float,
    remaining_months: int,
    closing_costs: float,
) -> dict:
    """Evaluate refinancing a mortgage to a new rate over the same remaining term.

    Both loans are treated as annuity loans over remaining_months.

    Args:
        current_balance: Outstanding loan balance, must be non-negative.
        current_rate_pct: Current annual interest rate in percent.
        new_rate_pct: Annual interest rate in percent after refinancing.
        remaining_months: Months left on the loan, must be positive.
        closing_costs: One-time cost of refinancing, must be non-negative.

    Returns:
        Dict with keys "monthly_savings" (old payment minus new payment),
        "breakeven_month" (first month where cumulative savings cover closing
        costs; None if monthly savings are not positive) and "total_savings"
        (savings over the remaining term net of closing costs). Money values
        are rounded to 2 decimals.
    """
    _validate_loan(current_balance, current_rate_pct, remaining_months)
    if new_rate_pct < 0:
        raise ValueError(f"new_rate_pct must be non-negative, got {new_rate_pct}")
    if closing_costs < 0:
        raise ValueError(f"closing_costs must be non-negative, got {closing_costs}")
    rate_now = _monthly_rate(current_rate_pct)
    rate_new = _monthly_rate(new_rate_pct)

    payment_now = _annuity_payment(current_balance, rate_now, remaining_months)
    payment_new = _annuity_payment(current_balance, rate_new, remaining_months)
    monthly_savings = payment_now - payment_new

    breakeven_month = (
        math.ceil(closing_costs / monthly_savings) if monthly_savings > 0 else None
    )
    total_savings = monthly_savings * remaining_months - closing_costs
    return {
        "monthly_savings": round(monthly_savings, 2),
        "breakeven_month": breakeven_month,
        "total_savings": round(total_savings, 2),
    }
