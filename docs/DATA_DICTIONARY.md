# Comprehensive Data Dictionary & Business KPI Mapping

## Dataset Overview

This dataset contains customer transaction records ingested daily from our CRM and transactional processing systems. It serves as the single source of truth for downstream customer behavioral analysis, segment profitability modeling, and churn prediction pipelines.

- **Source System**: CRM & Payment Processing Gateway
- **Last Updated**: 2025-05-21
- **Maintained By**: Data Engineering & Product Analytics Team
- **Update Frequency**: Daily Batch Pipeline

---

## Columns

### `customer_id`
- **Type**: Integer
- **Business Meaning**: Unique customer identifier assigned by the CRM system upon registration.
- **Example**: `12456`
- **Null Handling**: Never null (Primary key). If null, reject row at intake.
- **Related KPI**: Customer tracking, active customer count, customer lifetime value.
- **Updates**: Assigned once upon customer creation in CRM.

### `trnx_amt`
- **Type**: Float
- **Business Meaning**: Gross revenue generated from a single completed transaction.
- **Example**: `150.99`
- **Unit**: USD ($)
- **Null Handling**: Rare — investigate source payment gateway if null.
- **Related KPI**: Monthly revenue, average order value (AOV), segment revenue.
- **Updates**: Immutably recorded upon transaction completion.

### `purchase_date`
- **Type**: Datetime (ISO-8601)
- **Business Meaning**: Precise timestamp when the transaction was completed.
- **Example**: `2025-01-15T14:30:00Z`
- **Unit**: UTC Timezone
- **Null Handling**: Never null.
- **Related KPI**: Sales velocity, revenue velocity, cohort retention.
- **Updates**: Recorded automatically at checkout.

### `cust_segment`
- **Type**: String
- **Business Meaning**: Market classification determining customer account size and business model.
- **Valid Values**: `B2B` (Enterprise/Business), `B2C` (Retail Consumer), `SMB` (Small/Medium Business)
- **Example**: `B2B`
- **Null Handling**: If null, default to `UNKNOWN` and flag for CRM audit.
- **Related KPI**: Segment revenue, segment churn rate, segment profitability.
- **Updates**: Updated monthly via automated CRM customer scoring.

### `flag_churn`
- **Type**: Integer (Binary: `0` or `1`)
- **Business Meaning**: Indicator marking whether the customer churned within the 90 days following this transaction.
- **Example**: `0` (Retained) / `1` (Churned)
- **Null Handling**: Defaults to `0` if unknown.
- **Related KPI**: Churn rate, customer retention rate, 90-day predictive risk.
- **Updates**: Re-calculated quarterly based on transaction history gaps.

---

## Column to KPI Mapping

### 1. Monthly Revenue
- **Formula**: `SUM(trnx_amt)` filtered by calendar month
- **Related Columns**: `trnx_amt`, `purchase_date`
- **Why It Matters**: Tracks total top-line revenue performance against quarterly business targets.
- **Update Frequency**: Daily

### 2. Sales Velocity
- **Formula**: `COUNT(transaction_id) / total_days`
- **Related Columns**: `purchase_date`, `customer_id`
- **Why It Matters**: Measures sales activity volume, purchase frequency, and transactional momentum.
- **Update Frequency**: Weekly

### 3. Segment Revenue
- **Formula**: `SUM(trnx_amt)` grouped by `cust_segment`
- **Related Columns**: `trnx_amt`, `cust_segment`
- **Why It Matters**: Identifies top-performing customer tiers and guides go-to-market resource allocation.
- **Update Frequency**: Monthly

### 4. Churn Rate
- **Formula**: `SUM(flag_churn) / COUNT(DISTINCT customer_id)`
- **Related Columns**: `flag_churn`, `customer_id`
- **Why It Matters**: Primary customer retention metric indicating product health and customer attrition risk.
- **Update Frequency**: Quarterly

### 5. Customer Lifetime Value (CLV)
- **Formula**: `AVG(trnx_amt) * transaction_frequency * average_lifespan`
- **Related Columns**: `trnx_amt`, `customer_id`, `purchase_date`
- **Why It Matters**: Quantifies long-term customer value to inform acquisition cost (CAC) thresholds.
- **Update Frequency**: Monthly

---

## Ambiguous Columns & Resolutions

### Column: `flag_churn`
- **Original Ambiguity**: Does `flag_churn = 1` mean the customer is currently churned, or that they will churn in the future?
- **Resolved Meaning**: Binary indicator marking whether a customer failed to make a repeat purchase in the 90 days following the transaction date.
- **Business Interpretation**: Historical churn indicator used as the target label for predictive retention models.
- **Proposed Rename**: `has_churned_90d`
- **Risk If Misunderstood**: Machine learning models trained on improper churn windows produce inaccurate risk scores and misallocate retention budgets.

### Column: `cust_segment`
- **Original Ambiguity**: Is this market segment, customer support tier, product line category, or geographic region?
- **Resolved Meaning**: Customer market classification (`B2B`, `B2C`, `SMB`) driving pricing tiers and sales alignment.
- **Business Interpretation**: Categorizes customer purchasing power and sales service model requirements.
- **Proposed Rename**: `market_segment`
- **Risk If Misunderstood**: Aggregating revenue across misclassified categories distorts unit economics and segment profitability.

---

## Column Relationships & Business Impact

### 1. Revenue per Customer
- **Definition**: `SUM(trnx_amt)` grouped by `customer_id`
- **How It Matters**: Identifies high-value enterprise accounts for VIP retention campaigns and upsell outreach.
- **Example**: "The top 10% of customers generate 50% of total transactional revenue."
- **Related Columns**: `customer_id`, `trnx_amt`, `cust_segment`

### 2. Churn by Segment
- **Definition**: `SUM(flag_churn) / COUNT(customer_id)` grouped by `cust_segment`
- **How It Matters**: Pinpoints specific customer segments exhibiting high attrition risk requiring product or pricing intervention.
- **Example**: "The SMB segment exhibits a 25% churn rate compared to 10% for Enterprise B2B."
- **Related Columns**: `flag_churn`, `cust_segment`, `customer_id`

### 3. Revenue Velocity
- **Definition**: Rolling 30-day sum of `trnx_amt` over time
- **How It Matters**: Detects seasonal revenue acceleration or deceleration before end-of-quarter financial reporting.
- **Example**: "Monthly revenue velocity is trending upward by 15% quarter-over-quarter."
- **Related Columns**: `trnx_amt`, `purchase_date`

---

*Documented as the single source of truth for the analytics and data engineering team.*
