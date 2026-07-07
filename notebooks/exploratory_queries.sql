-- =========================================================
-- DAY 07: EXPLORATORY QUERIES FOR SPRINT 1 REVIEW
-- =========================================================

-- Query 1: Verify the Total Master Company Count
SELECT COUNT(*) AS total_companies 
FROM companies;

-- Query 2: Verify Total Row Counts for Core Financial Tables
SELECT 'profitandloss' AS table_name, COUNT(*) AS row_count FROM profitandloss
UNION ALL
SELECT 'balancesheet' AS table_name, COUNT(*) AS row_count FROM balancesheet
UNION ALL
SELECT 'cashflow' AS table_name, COUNT(*) AS row_count FROM cashflow;

-- Query 3: Check Sector Breakdown of Loaded Companies
SELECT broad_sector, COUNT(*) AS company_count 
FROM sectors 
GROUP BY broad_sector 
ORDER BY company_count DESC;

-- Query 4: Identify Companies with Less Than 5 Years of P&L History (DQ-16 Check)
SELECT company_id, COUNT(*) AS yrs_count 
FROM profitandloss 
GROUP BY company_id 
HAVING yrs_count < 5;

-- Query 5: Check Years of Coverage for a Sample Company (e.g., TECHM)
SELECT year, sales, net_profit 
FROM profitandloss 
WHERE company_id = 'TECHM' 
ORDER BY year ASC;

-- Query 6: Check Total Stock Price History Points
SELECT COUNT(*) AS total_price_records 
FROM stock_prices;

-- Query 7: Verify There Are Zero Orphaned Financial Records
PRAGMA foreign_key_check;