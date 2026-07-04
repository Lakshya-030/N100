import pytest
from src.analytics.cagr import calculate_cagr_value_and_flag

def test_cagr_normal_growth():
    val, flag = calculate_cagr_value_and_flag(100, 144, 2)
    assert val == 20.0
    assert flag is None
def test_cagr_normal_flat():
    val, flag = calculate_cagr_value_and_flag(100, 100, 5)
    assert val == 0.0
    assert flag is None
def test_cagr_turnaround_flag():
    val, flag = calculate_cagr_value_and_flag(-50, 100, 3)
    assert val is None
    assert flag == "TURNAROUND"
def test_cagr_decline_to_loss_flag():
    val, flag = calculate_cagr_value_and_flag(100, -20, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_both_negative_flag():
    val, flag = calculate_cagr_value_and_flag(-100, -50, 3)
    assert val is None
    assert flag == "BOTH_NEGATIVE"

def test_cagr_zero_base_flag():
    val, flag = calculate_cagr_value_and_flag(0, 100, 5)
    assert val is None
    assert flag == "ZERO_BASE"

def test_cagr_insufficient_missing_data():
    val, flag = calculate_cagr_value_and_flag(None, 100, 5)
    assert val is None
    assert flag == "INSUFFICIENT"

def test_cagr_insufficient_years():
    val, flag = calculate_cagr_value_and_flag(100, 150, 0)
    assert val is None
    assert flag == "INSUFFICIENT"
def test_cagr_boundary_near_zero_positive():
    val, flag = calculate_cagr_value_and_flag(0.01, 100, 1)
    assert val is not None
    assert flag is None
def test_cagr_boundary_end_zero_loss():
    val, flag = calculate_cagr_value_and_flag(100, 0, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"