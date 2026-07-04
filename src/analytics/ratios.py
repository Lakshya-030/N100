import sqlite3
import pandas as pd

# ==========================================
# DAY 08: CORE PROFITABILITY FUNCTIONS
# ==========================================

def calculate_net_profit_margin(net_profit, sales):
    if sales == 0:
        return None
    return (net_profit / sales) * 100

def calculate_operating_profit_margin(operating_profit, sales, db_opm):
    if sales == 0:
        return None
    calculated_opm = (operating_profit / sales) * 100
    if db_opm is not None:
        if abs(calculated_opm - db_opm) > 1:
            print(f"[-] WARNING: OPM mismatch! Calc: {calculated_opm:.2f}%, DB: {db_opm:.2f}%")
    return calculated_opm

def calculate_roe(net_profit, equity_capital, reserves):
    denominator = equity_capital + reserves
    if denominator <= 0:
        return None
    return (net_profit / denominator) * 100

def calculate_roce(ebit, equity_capital, reserves, borrowings, broad_sector=None):
    if broad_sector == "Financials":
        return None 
    denominator = equity_capital + reserves + borrowings
    if denominator <= 0:
        return None
    return (ebit / denominator) * 100

def calculate_roa(net_profit, total_assets):
    if total_assets == 0:
        return None
    return (net_profit / total_assets) * 100



# DAY 09 :LEVERAGE & EFFICIENCY FUNCTIONS


def calculate_debt_to_equity(borrowings, equity_capital, reserves):
    if borrowings == 0:
        return 0.0
    denominator = equity_capital + reserves
    if denominator <= 0:
        return None
        
    return borrowings / denominator

def calculate_interest_coverage(operating_profit, other_income, interest):
    if interest == 0:
        return None
    earnings = operating_profit + other_income
    return earnings / interest

def calculate_net_debt(borrowings, investments):
    return borrowings - investments

def calculate_asset_turnover(sales, total_assets):
    if total_assets == 0:
        return None
    return sales / total_assets



def main():
    conn = sqlite3.connect("data/nifty100.db")
    
    try:
        df_sec = pd.read_sql("SELECT company_id, broad_sector FROM companies;", conn)
    except Exception:
        df_sec = pd.DataFrame(columns=['company_id', 'broad_sector'])

    df_pl = pd.read_sql("SELECT company_id, year, sales, operating_profit, depreciation, net_profit, opm_percentage, interest, other_income FROM profitandloss;", conn)
    df_bs = pd.read_sql("SELECT company_id, year, equity_capital, reserves, borrowings, total_assets, investments FROM balancesheet;", conn)
    
    df = pd.merge(df_pl, df_bs, on=['company_id', 'year'])
    if not df_sec.empty:
        df = pd.merge(df, df_sec, on='company_id', how='left')
    else:
        df['broad_sector'] = None
        
    results = []
    for _, row in df.iterrows():
        sales = float(row['sales'])
        op_profit = float(row['operating_profit'])
        dep = float(row['depreciation']) if row['depreciation'] is not None else 0.0
        net_profit = float(row['net_profit'])
        eq_cap = float(row['equity_capital'])
        reserves = float(row['reserves']) if row['reserves'] is not None else 0.0
        borrowings = float(row['borrowings']) if row['borrowings'] is not None else 0.0
        total_assets = float(row['total_assets'])
        sector = row['broad_sector']
        
        interest = float(row['interest']) if row['interest'] is not None else 0.0
        other_income = float(row['other_income']) if row['other_income'] is not None else 0.0
        investments = float(row['investments']) if row['investments'] is not None else 0.0
        
        ebit = op_profit - dep
        
        npm = calculate_net_profit_margin(net_profit, sales)
        opm = calculate_operating_profit_margin(op_profit, sales, row['opm_percentage'])
        roe = calculate_roe(net_profit, eq_cap, reserves)
        roce = calculate_roce(ebit, eq_cap, reserves, borrowings, sector)
        roa = calculate_roa(net_profit, total_assets)
        
        de = calculate_debt_to_equity(borrowings, eq_cap, reserves)
        icr = calculate_interest_coverage(op_profit, other_income, interest)
        net_debt = calculate_net_debt(borrowings, investments)
        asset_turnover = calculate_asset_turnover(sales, total_assets)
        

        
        high_leverage_flag = False
        if de is not None and de > 5 and sector != "Financials":
            high_leverage_flag = True
            
        icr_label = None
        if interest == 0:
            icr_label = "Debt Free"
        icr_warning_flag = False
        if icr is not None and icr < 1.5:
            icr_warning_flag = True
        
        results.append({
            "company_id": row['company_id'],
            "year": row['year'],
            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "return_on_capital_employed_pct": roce,
            "return_on_assets_pct": roa,
            "debt_to_equity": de,
            "high_leverage_flag": int(high_leverage_flag),
            "interest_coverage_ratio": icr,
            "icr_label": icr_label,
            "icr_warning_flag": int(icr_warning_flag),
            "net_debt": net_debt,
            "asset_turnover": asset_turnover
        })
        
    df_results = pd.DataFrame(results)
    print("\n[+] Day 08 & 09 Ratios Engine Complete!")
    print(df_results[['company_id', 'year', 'debt_to_equity', 'icr_label', 'high_leverage_flag']].head(5).to_string(index=False))
    conn.close()

if __name__ == "__main__":
    main()