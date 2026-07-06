import pytest

from src.mortgage import (
    amortization_schedule,
    monthly_payment,
    payoff_simulation,
    refinance_breakeven,
)


# --- monthly_payment ---


def test_monthly_payment_annuity():
    # Classic reference case: 100k at 6% over 30 years.
    result = monthly_payment(100000, 6, 360, "annuity")
    assert result["monthly_payment"] == pytest.approx(599.55, abs=0.01)
    assert result["total_paid"] == pytest.approx(599.55 * 360, abs=1)
    assert result["total_interest"] == pytest.approx(result["total_paid"] - 100000, abs=0.01)


def test_monthly_payment_fixed_principal():
    # 100k at 12% over 12 months: principal part 8333.33,
    # first interest 1000.00, last interest 83.33.
    result = monthly_payment(100000, 12, 12, "fixed_principal")
    assert result["first_payment"] == pytest.approx(9333.33, abs=0.01)
    assert result["last_payment"] == pytest.approx(8416.67, abs=0.01)
    assert result["first_payment"] > result["last_payment"]
    assert result["average_payment"] == pytest.approx(8875.00, abs=0.01)


def test_monthly_payment_zero_rate():
    result = monthly_payment(120000, 0, 120, "annuity")
    assert result["monthly_payment"] == 1000.00
    assert result["total_interest"] == 0.00


def test_monthly_payment_invalid_inputs():
    with pytest.raises(ValueError):
        monthly_payment(-100000, 6, 360, "annuity")
    with pytest.raises(ValueError):
        monthly_payment(100000, 6, -360, "annuity")
    with pytest.raises(ValueError):
        monthly_payment(100000, 6, 360, "bullet")


# --- amortization_schedule ---


def test_amortization_schedule_annuity():
    schedule = amortization_schedule(100000, 6, 360, "annuity")
    assert len(schedule) == 360
    first, last = schedule[0], schedule[-1]
    assert first["month"] == 1
    assert first["interest_part"] == pytest.approx(500.00, abs=0.01)  # 100000 * 0.5%
    assert first["payment"] == pytest.approx(599.55, abs=0.01)
    assert last["remaining_balance"] == 0.00
    assert sum(row["principal_part"] for row in schedule) == pytest.approx(100000, abs=1)


def test_amortization_schedule_fixed_principal():
    schedule = amortization_schedule(100000, 12, 12, "fixed_principal")
    assert all(row["principal_part"] == pytest.approx(8333.33, abs=0.05) for row in schedule)
    assert schedule[0]["payment"] > schedule[-1]["payment"]
    assert schedule[-1]["remaining_balance"] == 0.00


def test_amortization_schedule_zero_rate():
    schedule = amortization_schedule(120000, 0, 120, "annuity")
    assert all(row["interest_part"] == 0.00 for row in schedule)
    assert all(row["payment"] == 1000.00 for row in schedule)
    assert schedule[-1]["remaining_balance"] == 0.00


def test_amortization_schedule_invalid_inputs():
    with pytest.raises(ValueError):
        amortization_schedule(100000, 6, 0, "annuity")
    with pytest.raises(ValueError):
        amortization_schedule(100000, 6, 360, "interest_only")


# --- payoff_simulation ---


def test_payoff_simulation_annuity():
    # 100 extra on the 599.55 reference loan pays it off in 252 months.
    result = payoff_simulation(100000, 6, 360, "annuity", 100)
    assert result["new_payoff_months"] == 252
    assert result["months_saved"] == 108
    assert result["interest_saved"] > 0
    assert result["interest_saved"] == pytest.approx(
        result["original_total_interest"] - result["new_total_interest"], abs=0.01
    )


def test_payoff_simulation_zero_rate():
    # 12k interest-free over 12 months, 1000 extra: 2000/month -> done in 6.
    result = payoff_simulation(12000, 0, 12, "annuity", 1000)
    assert result["new_payoff_months"] == 6
    assert result["months_saved"] == 6
    assert result["interest_saved"] == 0.00


def test_payoff_simulation_invalid_inputs():
    with pytest.raises(ValueError):
        payoff_simulation(100000, 6, 360, "annuity", -50)
    with pytest.raises(ValueError):
        payoff_simulation(-1, 6, 360, "annuity", 100)


# --- refinance_breakeven ---


def test_refinance_breakeven():
    # 100k, 6% -> 5% over 360 months: payments 599.55 -> 536.82.
    result = refinance_breakeven(100000, 6, 5, 360, 2000)
    assert result["monthly_savings"] == pytest.approx(62.73, abs=0.01)
    assert result["breakeven_month"] == 32  # ceil(2000 / 62.73)
    assert result["total_savings"] == pytest.approx(62.73 * 360 - 2000, abs=1)


def test_refinance_breakeven_zero_rate():
    # Refinancing 12k over 12 months down to 0%: new payment is exactly 1000.
    result = refinance_breakeven(12000, 6, 0, 12, 0)
    assert result["monthly_savings"] == pytest.approx(32.80, abs=0.01)
    assert result["breakeven_month"] == 0
    assert result["total_savings"] == pytest.approx(393.57, abs=0.01)


def test_refinance_breakeven_no_savings():
    # Refinancing to a higher rate never breaks even.
    result = refinance_breakeven(100000, 5, 6, 360, 2000)
    assert result["monthly_savings"] < 0
    assert result["breakeven_month"] is None


def test_refinance_breakeven_invalid_inputs():
    with pytest.raises(ValueError):
        refinance_breakeven(-100000, 6, 5, 360, 2000)
    with pytest.raises(ValueError):
        refinance_breakeven(100000, 6, 5, 360, -2000)
