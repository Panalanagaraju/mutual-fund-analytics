-- ============================================================
-- MUTUAL FUND ANALYTICS PLATFORM
-- DAY 2 - ANALYTICAL SQL QUERIES
-- ============================================================

-- ============================================================
-- QUERY 1
-- TOP 5 FUNDS BY AUM
-- ============================================================

SELECT
    fund_house,
    ROUND(MAX(aum_crore), 2) AS total_aum_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_crore DESC
LIMIT 5;


-- ============================================================
-- QUERY 2
-- AVERAGE NAV BY FUND
-- ============================================================

SELECT
    amfi_code,
    ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
GROUP BY amfi_code
ORDER BY avg_nav DESC;


-- ============================================================
-- QUERY 3
-- MONTHLY AVERAGE NAV
-- ============================================================

SELECT
    strftime('%Y-%m', nav_date) AS month,
    ROUND(AVG(nav), 2) AS avg_monthly_nav
FROM fact_nav
GROUP BY month
ORDER BY month;


-- ============================================================
-- QUERY 4
-- SIP YOY GROWTH ANALYSIS
-- ============================================================

SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;


-- ============================================================
-- QUERY 5
-- TRANSACTIONS BY STATE
-- ============================================================

SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;


-- ============================================================
-- QUERY 6
-- FUNDS WITH EXPENSE RATIO LESS THAN 1%
-- ============================================================

SELECT
    d.scheme_name,
    d.fund_house,
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund d
    ON p.amfi_code = d.amfi_code
WHERE p.expense_ratio_pct < 1
ORDER BY p.expense_ratio_pct;


-- ============================================================
-- QUERY 7
-- TOP 10 FUNDS BY 5 YEAR RETURN
-- ============================================================

SELECT
    d.scheme_name,
    d.fund_house,
    p.return_5yr_pct
FROM fact_performance p
JOIN dim_fund d
    ON p.amfi_code = d.amfi_code
ORDER BY p.return_5yr_pct DESC
LIMIT 10;


-- ============================================================
-- QUERY 8
-- CATEGORY WISE NET INFLOWS
-- ============================================================

SELECT
    category,
    ROUND(SUM(net_inflow_crore), 2) AS total_inflow
FROM fact_category_inflows
GROUP BY category
ORDER BY total_inflow DESC;


-- ============================================================
-- QUERY 9
-- AVERAGE RETURN BY CATEGORY
-- ============================================================

SELECT
    d.category,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_3yr_return
FROM fact_performance p
JOIN dim_fund d
    ON p.amfi_code = d.amfi_code
GROUP BY d.category
ORDER BY avg_3yr_return DESC;


-- ============================================================
-- QUERY 10
-- MOST POPULAR TRANSACTION TYPES
-- ============================================================

SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;


-- ============================================================
-- BONUS QUERY 11
-- TOP STATES BY INVESTMENT AMOUNT
-- ============================================================

SELECT
    state,
    ROUND(SUM(amount_inr), 2) AS investment_amount
FROM fact_transactions
GROUP BY state
ORDER BY investment_amount DESC
LIMIT 10;


-- ============================================================
-- BONUS QUERY 12
-- HIGHEST SHARPE RATIO FUNDS
-- ============================================================

SELECT
    d.scheme_name,
    d.fund_house,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund d
    ON p.amfi_code = d.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 10;