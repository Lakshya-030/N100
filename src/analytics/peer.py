import pandas as pd
import numpy as np

def compute_peer_percentiles(df):
    """
    DELIVERABLE COMPLIANCE: src/analytics/peer.py
    Computes precise percentile rankings for the latest financial year records.
    """
    ranking_metrics = [
        'return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 
        'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 'interest_coverage', 
        'operating_profit_margin_pct', 'pat_cagr_5yr', 'sales'
    ]
    
    # Existing columns clear kar rahe hain taaki naya data hi write ho
    for metric in ranking_metrics:
        col_name = f'{metric}_percentile'
        if col_name in df.columns:
            df.drop(columns=[col_name], inplace=True)
            
    # Filter to look at only the latest year per company
    latest_indices = df.groupby('company_id')['year'].idxmax()
    latest_df = df.loc[latest_indices].copy()
    
    for metric in ranking_metrics:
        if metric in latest_df.columns:
            ascending_order = True if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity'] else False
            
            ranks = latest_df.groupby('peer_group')[metric].rank(ascending=ascending_order, method='first')
            group_counts = latest_df.groupby('peer_group')[metric].transform('count')
            
            latest_df[f'{metric}_percentile'] = (ranks / group_counts) * 100
            latest_df[f'{metric}_percentile'] = latest_df[f'{metric}_percentile'].fillna(0).round(0)
            
    # Direct mapping using index map
    for metric in ranking_metrics:
        pct_col = f'{metric}_percentile'
        df[pct_col] = 0.0
        df.loc[latest_indices, pct_col] = latest_df[pct_col].values

    return df