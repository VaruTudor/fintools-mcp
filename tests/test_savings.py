import pytest

from src.savings import compound_savings, emergency_fund_target, real_return


# --- compound_savings ---


def test_compound_savings():
    # 100/month at 12% (1%/month) for a year: FV = 100 * ((1.01^12 - 1) / 0.01) = 1268.25.
    result = compound_savings(100, 12, 12, 0)
    assert result["end_balance"] == pytest.approx(1268.25, abs=0.01)
    assert result["total_deposited"] == 1200.00
    assert result["total_interest"] == pytest.approx(68.25, abs=0.01)


def test_compound_savings_with_initial():
    # 1000 initial at 12% for a year, no deposits: 1000 * 1.01^12 = 1126.83.
    result = compound_savings(0, 12, 12, 1000)
    assert result["end_balance"] == pytest.approx(1126.83, abs=0.01)
    assert result["total_deposited"] == 1000.00


def test_compound_savings_zero_rate():
    result = compound_savings(100, 0, 12, 500)
    assert result["end_balance"] == 1700.00
    assert result["total_deposited"] == 1700.00
    assert result["total_interest"] == 0.00


def test_compound_savings_invalid_inputs():
    with pytest.raises(ValueError):
        compound_savings(-100, 12, 12, 0)
    with pytest.raises(ValueError):
        compound_savings(100, 12, 0, 0)
    with pytest.raises(ValueError):
        compound_savings(100, 12, 12, -1)


# --- emergency_fund_target ---


def test_emergency_fund_target():
    # 2000/month expenses, 6 months coverage, 3000 saved, 500/month contribution.
    result = emergency_fund_target(2000, 6, 3000, 500)
    assert result["target_amount"] == 12000.00
    assert result["gap"] == 9000.00
    assert result["months_to_target"] == 18


def test_emergency_fund_target_already_reached():
    result = emergency_fund_target(2000, 6, 15000, 500)
    assert result["gap"] == 0.00
    assert result["months_to_target"] == 0


def test_emergency_fund_target_zero_contribution():
    # Positive gap with zero contribution is never reached.
    result = emergency_fund_target(2000, 6, 3000, 0)
    assert result["gap"] == 9000.00
    assert result["months_to_target"] is None


def test_emergency_fund_target_invalid_inputs():
    with pytest.raises(ValueError):
        emergency_fund_target(-2000, 6, 3000, 500)
    with pytest.raises(ValueError):
        emergency_fund_target(2000, 0, 3000, 500)
    with pytest.raises(ValueError):
        emergency_fund_target(2000, 6, 3000, -500)


# --- real_return ---


def test_real_return():
    # Fisher: 1.06 / 1.02 - 1 = 3.9216%; approximation: 6 - 2 = 4%.
    result = real_return(6, 2)
    assert result["real_rate_exact_pct"] == pytest.approx(3.9216, abs=0.0001)
    assert result["real_rate_approx_pct"] == 4.0


def test_real_return_zero_inflation():
    result = real_return(6, 0)
    assert result["real_rate_exact_pct"] == 6.0
    assert result["real_rate_approx_pct"] == 6.0


def test_real_return_invalid_inputs():
    with pytest.raises(ValueError):
        real_return(6, -100)
    with pytest.raises(ValueError):
        real_return(6, -150)
