Mutual Fund Analytics Platform
Data Dictionary
Introduction
This document describes the datasets used in the Mutual Fund Analytics Platform project. It provides details about each dataset, column definitions, data types, and business meaning. The data dictionary serves as a reference for understanding the data model used in analysis, reporting, and dashboard development.

1. Fund Master Dataset
   File: 01_fund_master.csv
   Purpose: Contains master information about mutual fund schemes.
   Column Type Description
   amfi_code Integer Unique AMFI scheme identifier
   fund_house String Asset Management Company (AMC) name
   scheme_name String Name of the mutual fund scheme
   category String Fund category (Equity, Debt, etc.)
   sub_category String Detailed category such as Large Cap, Small Cap
   plan String Direct or Regular plan
   launch_date Date Scheme launch date
   benchmark String Benchmark index
   expense_ratio_pct Float Annual expense ratio
   exit_load_pct Float Exit load percentage
   min_sip_amount Integer Minimum SIP amount
   min_lumpsum_amount Integer Minimum lump sum amount
   fund_manager String Fund manager name
   risk_category String Risk classification
   sebi_category_code String SEBI category code

2. NAV History Dataset
   File: 02_nav_history.csv
   Purpose: Stores historical Net Asset Value (NAV) data.
   Column Type Description
   amfi_code Integer Scheme identifier
   date Date NAV date
   nav Float Net Asset Value

3. AUM Dataset
   File: 03_aum_by_fund_house.csv
   Purpose: Tracks Assets Under Management (AUM) by fund house.
   Column Type Description
   date Date Reporting date
   fund_house String Fund house name
   aum_lakh_crore Float AUM in lakh crore
   aum_crore Integer AUM in crore
   num_schemes Integer Number of schemes

4. Monthly SIP Inflows
   File: 04_monthly_sip_inflows.csv
   Purpose: Monthly SIP investment trends.
   Column Type Description
   month String Reporting month
   sip_inflow_crore Integer SIP inflow amount
   active_sip_accounts_crore Float Active SIP accounts
   new_sip_accounts_lakh Float New SIP accounts
   sip_aum_lakh_crore Float SIP AUM
   yoy_growth_pct Float Year-on-year growth percentage

5. Category Inflows
   File: 05_category_inflows.csv
   Purpose: Category-wise fund inflows.
   Column Type Description
   month String Reporting month
   category String Mutual fund category
   net_inflow_crore Float Net inflow amount

6. Industry Folio Count
   File: 06_industry_folio_count.csv
   Purpose: Industry-level investor folio statistics.
   Column Type Description
   month String Reporting month
   total_folios_crore Float Total investor folios
   equity_folios_crore Float Equity folios
   debt_folios_crore Float Debt folios
   hybrid_folios_crore Float Hybrid folios
   others_folios_crore Float Other folios

7. Scheme Performance
   File: 07_scheme_performance.csv
   Purpose: Mutual fund return and risk metrics.
   Column Type Description
   amfi_code Integer Scheme identifier
   return_1yr_pct Float One-year return
   return_3yr_pct Float Three-year return
   return_5yr_pct Float Five-year return
   alpha Float Alpha value
   beta Float Beta value
   sharpe_ratio Float Sharpe ratio
   sortino_ratio Float Sortino ratio
   std_dev_ann_pct Float Standard deviation
   max_drawdown_pct Float Maximum drawdown
   expense_ratio_pct Float Expense ratio
   morningstar_rating Integer Morningstar rating
   risk_grade String Risk grade

8. Investor Transactions
   File: 08_investor_transactions.csv
   Purpose: Records investor transaction activity.
   Column Type Description
   investor_id String Investor identifier
   transaction_date Date Transaction date
   amfi_code Integer Scheme code
   transaction_type String SIP, Lumpsum, Redemption
   amount_inr Integer Transaction amount
   state String Investor state
   city String Investor city
   city_tier String Tier classification
   age_group String Age category
   gender String Investor gender
   annual_income_lakh Float Annual income
   payment_mode String Payment method
   kyc_status String KYC verification status

9. Portfolio Holdings
   File: 09_portfolio_holdings.csv
   Purpose: Underlying holdings of mutual fund schemes.
   Column Type Description
   amfi_code Integer Scheme identifier
   stock_symbol String Stock ticker
   stock_name String Company name
   sector String Industry sector
   weight_pct Float Portfolio allocation
   market_value_cr Float Market value
   current_price_inr Float Current stock price
   portfolio_date Date Portfolio disclosure date

10. Benchmark Indices
    File: 10_benchmark_indices.csv
    Purpose: Benchmark index values used for comparison.
    Column Type Description
    date Date Trading date
    index_name String Benchmark index
    close_value Float Closing index value

Data Quality Summary
A comprehensive validation was performed on all datasets during the cleaning process. Most datasets contained no missing values and no duplicate records. The Monthly SIP Inflows dataset contained 12 missing values in the YoY Growth Percentage column, which is expected due to unavailable historical comparison data. All datasets were standardized, validated, and successfully loaded into the SQLite database for further analysis.

Data Dictionary

1. Fund Master
File: 01_fund_master.csv
Column	Data Type	Description
amfi_code	Integer	Unique AMFI scheme identifier
fund_house	Text	Asset Management Company (AMC) name
scheme_name	Text	Mutual fund scheme name
category	Text	Broad fund category (Equity, Debt)
sub_category	Text	Large Cap, Small Cap, ELSS, etc.
plan	Text	Direct or Regular plan
launch_date	Date	Scheme launch date
benchmark	Text	Benchmark index used for comparison
expense_ratio_pct	Float	Annual expense ratio percentage
exit_load_pct	Float	Exit load percentage
min_sip_amount	Integer	Minimum SIP investment amount
min_lumpsum_amount	Integer	Minimum lump sum investment amount
fund_manager	Text	Name of fund manager
risk_category	Text	Risk classification of scheme
sebi_category_code	Text	SEBI category code

2. NAV History
File: 02_nav_history.csv
Column	Data Type	Description
amfi_code	Integer	Unique scheme identifier
date	Date	NAV reporting date
nav	Float	Net Asset Value of scheme

3. AUM by Fund House
File: 03_aum_by_fund_house.csv
Column	Data Type	Description
date	Date	Reporting date
fund_house	Text	Fund house name
aum_lakh_crore	Float	Assets Under Management in lakh crore
aum_crore	Integer	Assets Under Management in crore
num_schemes	Integer	Total schemes managed

4. Monthly SIP Inflows
File: 04_monthly_sip_inflows.csv
Column	Data Type	Description
month	Text	Reporting month
sip_inflow_crore	Integer	Monthly SIP inflow amount
active_sip_accounts_crore	Float	Active SIP accounts
new_sip_accounts_lakh	Float	Newly opened SIP accounts
sip_aum_lakh_crore	Float	SIP assets under management
yoy_growth_pct	Float	Year-over-year growth percentage

5. Category Inflows
File: 05_category_inflows.csv
Column	Data Type	Description
month	Text	Reporting month
category	Text	Fund category
net_inflow_crore	Float	Net inflow amount in crore rupees

6. Industry Folio Count
File: 06_industry_folio_count.csv
Column	Data Type	Description
month	Text	Reporting month
total_folios_crore	Float	Total investor folios
equity_folios_crore	Float	Equity fund folios
debt_folios_crore	Float	Debt fund folios
hybrid_folios_crore	Float	Hybrid fund folios
others_folios_crore	Float	Other category folios

7. Scheme Performance
File: 07_scheme_performance.csv
Column	Data Type	Description
amfi_code	Integer	Unique scheme identifier
scheme_name	Text	Name of scheme
fund_house	Text	Asset Management Company
category	Text	Fund category
plan	Text	Direct or Regular
return_1yr_pct	Float	One year return percentage
return_3yr_pct	Float	Three year return percentage
return_5yr_pct	Float	Five year return percentage
benchmark_3yr_pct	Float	Three year benchmark return
alpha	Float	Excess return over benchmark
beta	Float	Volatility relative to benchmark
sharpe_ratio	Float	Risk-adjusted return metric
sortino_ratio	Float	Downside risk-adjusted return metric
std_dev_ann_pct	Float	Annualized standard deviation
max_drawdown_pct	Float	Maximum decline from peak
aum_crore	Integer	Scheme AUM in crore
expense_ratio_pct	Float	Expense ratio percentage
morningstar_rating	Integer	Morningstar rating
risk_grade	Text	Risk grade classification

8. Investor Transactions
File: 08_investor_transactions.csv
Column	Data Type	Description
investor_id	Text	Unique investor identifier
transaction_date	Date	Transaction date
amfi_code	Integer	Scheme identifier
transaction_type	Text	SIP, Lumpsum or Redemption
amount_inr	Integer	Transaction amount in INR
state	Text	Investor state
city	Text	Investor city
city_tier	Text	Tier classification of city
age_group	Text	Investor age bracket
gender	Text	Investor gender
annual_income_lakh	Float	Annual income in lakh rupees
payment_mode	Text	Payment method used
kyc_status	Text	KYC verification status

9. Portfolio Holdings
File: 09_portfolio_holdings.csv
Column	Data Type	Description
amfi_code	Integer	Scheme identifier
stock_symbol	Text	Stock ticker symbol
stock_name	Text	Company name
sector	Text	Industry sector
weight_pct	Float	Portfolio allocation percentage
market_value_cr	Float	Market value in crore rupees
current_price_inr	Float	Current stock price
portfolio_date	Date	Portfolio reporting date

10. Benchmark Indices
File: 10_benchmark_indices.csv
Column	Data Type	Description
date	Date	Trading date
index_name	Text	Benchmark index name
close_value	Float	Index closing value

Data Quality Summary
Dataset	Rows	Columns	Missing Values
01_fund_master.csv	40	15	0
02_nav_history.csv	46000	3	0
03_aum_by_fund_house.csv	90	5	0
04_monthly_sip_inflows.csv	48	6	12
05_category_inflows.csv	144	3	0
06_industry_folio_count.csv	21	6	0
07_scheme_performance.csv	40	19	0
08_investor_transactions.csv	32778	13	0
09_portfolio_holdings.csv	322	8	0
10_benchmark_indices.csv	8050	3	0

Conclusion
The Mutual Fund Analytics Platform datasets provide comprehensive information related to mutual fund schemes, NAV history, AUM statistics, SIP inflows, investor behavior, portfolio holdings, and benchmark performance. These datasets were cleaned, validated, and loaded into the SQLite data warehouse for analytical reporting and dashboard development.

