import os
import pandas as pd

# THE 16 INDIVIDUAL RULE TOOLS (Your exact simple functions)


def check_uniqueness(df, table_name, failures):
    if table_name == 'companies' and 'id' in df.columns:
        if df['id'].duplicated().any():
            for dup in df['id'][df['id'].duplicated()].unique():
                failures.append({"company_id": str(dup), "year": "SNAPSHOT", "field": "id", "issue": "DQ-01: Duplicate company id found", "severity": "CRITICAL"})
                
    if table_name in ['profitandloss', 'balancesheet', 'cashflow'] and 'company_id' in df.columns and 'year' in df.columns:
        if df.duplicated(subset=['company_id', 'year']).any():
            failures.append({"company_id": "MULTIPLE", "year": "MULTIPLE", "field": "company_id, year", "issue": "DQ-02: Duplicate company-year records found", "severity": "CRITICAL"})

def check_foreign_key(df, table_name, valid_company_ids, failures):
    if valid_company_ids and 'company_id' in df.columns:
        for _, row in df.iterrows():
            co_id = str(row['company_id'])
            if co_id not in valid_company_ids:
                failures.append({"company_id": co_id, "year": str(row.get('year', 'SNAPSHOT')), "field": "company_id", "issue": "DQ-03: Outside our 92 master list (Orphan Row)", "severity": "CRITICAL"})

def check_balance_sheet(df, table_name, failures):
    if table_name == 'balancesheet' and all(c in df.columns for c in ["total_assets", "total_liabilities"]):
        for _, row in df.iterrows():
            if abs(row["total_assets"] - row["total_liabilities"]) > 1:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "total_assets", "issue": "DQ-04: Balance sheet assets and liabilities mismatch", "severity": "WARNING"})

def check_opm(df, table_name, failures):
    if table_name == 'profitandloss' and all(c in df.columns for c in ['sales', 'operating_profit', 'opm_percentage']):
        for _, row in df.iterrows():
            sales, op, opm = row['sales'], row['operating_profit'], row['opm_percentage']
            if sales > 0 and abs(opm) <= 100:
                calc_opm = (op / sales) * 100
                if abs(calc_opm - opm) > 1:
                    failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "opm_percentage", "issue": "DQ-05: Pre-computed OPM percentage mismatch", "severity": "WARNING"})

def check_positive_sales(df, table_name, failures):
    if 'sales' in df.columns:
        for _, row in df.iterrows():
            if row['sales'] <= 0:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "sales", "issue": "DQ-06: Sales value is zero or negative", "severity": "WARNING"})

def check_year_parse_error(df, failures):
    if "year" in df.columns:
        for _, row in df.iterrows():
            if str(row['year']) == 'PARSE ERROR':
                failures.append({"company_id": str(row.get('company_id', 'UNKNOWN')), "year": "PARSE ERROR", "field": "year", "issue": "DQ-07: Year parser could not read original text layout", "severity": "WARNING"})

def check_missing_ticker(df, failures):
    if "company_id" in df.columns:
        for _, row in df.iterrows():
            if str(row["company_id"]) == "MISSING":
                failures.append({"company_id": "MISSING", "year": str(row.get('year', 'UNKNOWN')), "field": "company_id", "issue": "DQ-08: Ticker was completely blank or missing in source", "severity": "WARNING"})

def check_cashflow(df, table_name, failures):
    if table_name == 'cashflow' and all(c in df.columns for c in ["operating_activity", "investing_activity", "financing_activity", "net_cash_flow"]):
        for _, row in df.iterrows():
            calc_cf = row["operating_activity"] + row["investing_activity"] + row["financing_activity"]
            if abs(calc_cf - row["net_cash_flow"]) > 1:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "net_cash_flow", "issue": "DQ-09: Cash flow components do not sum to net cash flow", "severity": "WARNING"})

def check_fixed_assets(df, table_name, failures):
    if table_name == 'balancesheet' and "fixed_assets" in df.columns:
        for _, row in df.iterrows():
            if row["fixed_assets"] < 0:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "fixed_assets", "issue": "DQ-10: Negative fixed assets detected", "severity": "WARNING"})

def check_tax_rate(df, table_name, failures):
    if table_name == 'profitandloss' and "tax_percentage" in df.columns:
        for _, row in df.iterrows():
            if row["tax_percentage"] < 0 or row["tax_percentage"] > 60:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "tax_percentage", "issue": "DQ-11: Tax rate out of normal 0-60% range boundaries", "severity": "WARNING"})

def check_dividend_payout(df, failures):
    if "dividend_payout" in df.columns:
        for _, row in df.iterrows():
            if row["dividend_payout"] > 200:
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "dividend_payout", "issue": "DQ-12: Unreasonable dividend payout ratio outlier", "severity": "WARNING"})

def check_url(df, table_name, failures):
    if table_name == 'documents' and "Annual_Report" in df.columns:
        for _, row in df.iterrows():
            if not str(row["Annual_Report"]).startswith("http"):
                failures.append({"company_id": str(row['company_id']), "year": str(row.get('Year', 'UNKNOWN')), "field": "Annual_Report", "issue": "DQ-13: Missing standard link web protocol prefix", "severity": "WARNING"})

def check_eps_sign(df, table_name, failures):
    if table_name == 'profitandloss' and all(c in df.columns for c in ["net_profit", "eps"]):
        for _, row in df.iterrows():
            np, eps = row["net_profit"], row["eps"]
            if (np > 0 and eps < 0) or (np < 0 and eps > 0):
                failures.append({"company_id": str(row['company_id']), "year": str(row['year']), "field": "eps", "issue": "DQ-14: Mathematical sign gap between Net Profit and EPS columns", "severity": "WARNING"})

def check_history_coverage(df, table_name, failures):
    if table_name in ['profitandloss', 'balancesheet', 'cashflow'] and 'company_id' in df.columns and 'year' in df.columns:
        for company, group in df.groupby("company_id"):
            if len(group["year"].unique()) < 5:
                failures.append({"company_id": str(company), "year": "ALL", "field": "year", "issue": "DQ-16: Company has under 5 tracking years of history layout", "severity": "WARNING"})


# THE MASTER ENGINES (The Conductor and the Exporter)

def run_data_quality_checks(df: pd.DataFrame, table_name: str, valid_tickers: set = None) -> list:
    """The master gatekeeper function that executes our individual checks systematically."""
    failures = []
    if df.empty:
        return failures
        
    # We call your individual functions one-by-one, passing our master list down
    check_uniqueness(df, table_name, failures)
    check_foreign_key(df, table_name, valid_tickers, failures)
    check_balance_sheet(df, table_name, failures)
    check_opm(df, table_name, failures)
    check_positive_sales(df, table_name, failures)
    check_year_parse_error(df, failures)
    check_missing_ticker(df, failures)
    check_cashflow(df, table_name, failures)
    check_fixed_assets(df, table_name, failures)
    check_tax_rate(df, table_name, failures)
    check_dividend_payout(df, failures)
    check_url(df, table_name, failures)
    check_eps_sign(df, table_name, failures)
    check_history_coverage(df, table_name, failures)
    
    return failures


def save_validation_failures(all_failures: list, output_dir: str = "output"):
    """Turns the error dictionaries into a structured spreadsheet with correct columns."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "validation_failures.csv")
    
    if not all_failures:
        pd.DataFrame(columns=["company_id", "year", "field", "issue", "severity"]).to_csv(output_path, index=False)
        return

    # Pandas converts our clean notes directly into table columns
    df_errors = pd.DataFrame(all_failures)
    df_errors.to_csv(output_path, index=False)
    print(f"[+] Logged errors cleanly to: {output_path}")