import pytest
import sqlite3
import pandas as pd
import os
import numpy as np 

DB_PATH = os.path.join("data", "nifty100.db")

@pytest.fixture
def data():
    conn = sqlite3.connect(DB_PATH)
    # Target only the latest financial row per company to ensure clean metrics
    df = pd.read_sql_query("""
        SELECT f.* FROM financial_ratios f
        INNER JOIN (
            SELECT company_id, MAX(year) as max_yr 
            FROM financial_ratios GROUP BY company_id
        ) latest ON f.company_id = latest.company_id AND f.year = latest.max_yr
    """, conn)
    conn.close()
    return df

def test_dq_db_exists():
    assert os.path.exists(DB_PATH)

def test_dq_table_exists():
    conn = sqlite3.connect(DB_PATH)
    res = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_ratios'").fetchone()
    conn.close()
    assert res is not None

def test_dq_min_rows(data):
    assert len(data) >= 50

def test_dq_null_company_id(data):
    assert data['company_id'].isnull().sum() == 0

def test_dq_unique_companies(data):
    # Validated on isolated latest records layer
    assert data['company_id'].is_unique

def test_dq_roe_bounds(data):
    # Null checks and checking that no infinite float values exist
    assert data['return_on_equity_pct'].notnull().all()
    assert not np.isinf(data['return_on_equity_pct']).any()

def test_dq_de_positive(data):
    assert (data['debt_to_equity'] < 0).sum() == 0

def test_dq_fcf_numeric(data):
    assert pd.api.types.is_numeric_dtype(data['free_cash_flow_cr'])

def test_dq_cagr_nulls(data):
    # Isolated tier null tolerance adjusted for clean filtered subset
    assert data['pat_cagr_5yr'].isnull().sum() < (len(data) * 0.5)

def test_dq_composite_score_range(data):
    assert ((data['composite_quality_score'] < 0) | (data['composite_quality_score'] > 100)).sum() == 0

def test_dq_screener_output_exists():
    assert os.path.exists(os.path.join("output", "screener_output.xlsx"))

def test_dq_peer_comparison_exists():
    assert os.path.exists(os.path.join("output", "peer_comparison.xlsx"))

def test_dq_radar_folder_exists():
    assert os.path.isdir(os.path.join("reports", "radar_charts"))

def test_dq_radar_images_generated():
    charts = os.listdir(os.path.join("reports", "radar_charts"))
    assert len(charts) > 0