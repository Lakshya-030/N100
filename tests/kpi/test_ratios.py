import pytest
from src.analytics.ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
    calculate_roa,
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_asset_turnover
)

# ==========================================
# DAY 08 TESTS (PROFITABILITY)
# ==========================================

def test_normal_net_profit_margin():
    assert calculate_net_profit_margin(10, 100) == 10.0

def test_zero_sales_npm():
    assert calculate_net_profit_margin(10, 0) is None

def test_normal_roe():
    assert calculate_roe(20, 50, 50) == 20.0

def test_negative_equity_roe():
    assert calculate_roe(10, -50, 10) is None

def test_zero_equity_roce():
    assert calculate_roce(15, 0, 0, 0, broad_sector="Manufacturing") is None

def test_financial_sector_roce():
    assert calculate_roce(100, 50, 50, 200, broad_sector="Financials") is None

def test_zero_assets_roa():
    assert calculate_roa(10, 0) is None

def test_opm_normal_calculation():
    assert calculate_operating_profit_margin(20, 100, 20) == 20.0


# ==========================================
# DAY 09 TESTS (LEVERAGE & EFFICIENCY) - NEW
# ==========================================

# Test 1: Normal Debt to Equity calculation
def test_de_ratio_normal_calculation():
    # borrowings = 50, equity_capital = 60, reserves = 40 -> 50 / (60 + 40) = 0.5
    result = calculate_debt_to_equity(50, 60, 40)
    assert result == 0.5

# Test 2: D/E rule where borrowings = 0 returns 0 (not None)
def test_de_ratio_returns_zero_when_borrowings_are_zero():
    result = calculate_debt_to_equity(0, 60, 40)
    assert result == 0.0

# Test 3: D/E rule where equity pool <= 0 returns None
def test_de_ratio_returns_none_on_negative_equity():
    result = calculate_debt_to_equity(100, -50, 20)
    assert result is None

# Test 4: ICR rule where interest = 0 returns None
def test_icr_returns_none_when_interest_is_zero():
    result = calculate_interest_coverage(100, 20, 0)
    assert result is None

# Test 5: ICR normal calculation
def test_icr_normal_calculation():
    # (operating_profit 80 + other_income 20) / interest 20 = 100 / 20 = 5.0
    result = calculate_interest_coverage(80, 20, 20)
    assert result == 5.0

# Test 6: Net Debt basic subtraction
def test_net_debt_simple_subtraction():
    # borrowings = 200, investments = 50 -> 200 - 50 = 150
    result = calculate_net_debt(200, 50)
    assert result == 150

# Test 7: Asset turnover boundary rule for zero assets
def test_asset_turnover_returns_none_on_zero_assets():
    result = calculate_asset_turnover(500, 0)
    assert result is None

# Test 8: Asset turnover standard operation
def test_asset_turnover_normal_calculation():
    # sales = 300, total_assets = 100 -> 300 / 100 = 3.0
    result = calculate_asset_turnover(300, 100)
    assert result == 3.0