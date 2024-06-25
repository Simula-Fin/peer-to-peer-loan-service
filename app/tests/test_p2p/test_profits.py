import pytest
from math import pow
from app.helpers.p2p_utils import ProfitCalculator

@pytest.mark.asyncio
async def test_calculate_profits():
    investment_amount = 10000.0
    rate_juros = 5.0
    duration = 12
    expected_bank_profit_rate = 0.2

    bank_profit, investor_profit, monthly_payment = ProfitCalculator.calculate_profits(investment_amount, rate_juros, duration)

    i = rate_juros / 100
    expected_monthly_payment = investment_amount * (i * pow(1 + i, duration)) / (pow(1 + i, duration) - 1)
    expected_total_payment = expected_monthly_payment * duration
    expected_total_interest = expected_total_payment - investment_amount
    expected_bank_profit = expected_total_interest * expected_bank_profit_rate
    expected_investor_profit = expected_total_interest - expected_bank_profit

    assert bank_profit == expected_bank_profit
    assert investor_profit == expected_investor_profit
    assert monthly_payment == expected_monthly_payment