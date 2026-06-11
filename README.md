# End-to-End E-Commerce Analytics Platform

[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=flat&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-MotherDuck-FFC72C?style=flat&logo=duckdb&logoColor=black)](https://motherduck.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://dbtanalytics-n9yv9r9bmfkqodl2reemnk.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-krutispatil-181717?style=flat&logo=github&logoColor=white)](https://github.com/krutispatil)

> **Live Dashboard →** https://dbtanalytics-n9yv9r9bmfkqodl2reemnk.streamlit.app/

---

## Overview

A production-grade ELT analytics pipeline built on real-world Brazilian e-commerce data from [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (100,245 orders · 2016–2018).

Raw CSV data is loaded into **MotherDuck** (cloud DuckDB), transformed through a **4-layer dbt Core pipeline**, validated with **44 automated data tests**, and served through a live **Streamlit dashboard** — covering revenue trends, customer segmentation, seller performance, and delivery SLA analysis.

---

## Architecture

```
Raw CSVs (Kaggle Olist)
        │
        ▼
┌─────────────────┐
│   MotherDuck    │  Cloud DuckDB warehouse
│  schema: main   │  8 raw source tables
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Staging      │  8 views · schema: dbt_kpatil
│  stg_* models   │  Type casting, deduplication,
│                 │  null handling, column renaming
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Intermediate   │  3 views · schema: dbt_kpatil
│  int_* models   │  Multi-table joins, business logic,
│                 │  customer segmentation, enrichment
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Marts       │  4 tables · schema: dbt_kpatil
│  mart_* models  │  Aggregated, analytics-ready KPIs
│                 │  for revenue, customers, sellers,
│                 │  and delivery
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Streamlit    │  Live dashboard
│   Dashboard     │  5 pages · 20+ charts
└─────────────────┘
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Warehouse | MotherDuck (cloud DuckDB) |
| Transformation | dbt Core 1.8 + dbt-duckdb 1.10.1 |
| Orchestration | Manual / GitHub Codespaces |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.11 |
| Version Control | GitHub |

---

## dbt Project Structure

```
my_pipeline/
├── dbt_project.yml
├── profiles.yml          ← at ~/.dbt/profiles.yml
└── models/
    ├── staging/          ← 8 views
    │   ├── sources.yml
    │   ├── schema.yml    ← 26 tests
    │   ├── stg_orders.sql
    │   ├── stg_customers.sql
    │   ├── stg_order_items.sql
    │   ├── stg_payments.sql
    │   ├── stg_products.sql
    │   ├── stg_sellers.sql
    │   ├── stg_reviews.sql
    │   └── stg_product_category_translations.sql
    ├── intermediate/     ← 3 views
    │   ├── schema.yml    ← 8 tests
    │   ├── int_orders_enriched.sql
    │   ├── int_customer_orders.sql
    │   └── int_seller_performance.sql
    └── marts/            ← 4 tables
        ├── schema.yml    ← 10 tests
        ├── mart_sales.sql
        ├── mart_customers.sql
        ├── mart_sellers.sql
        └── mart_delivery.sql
```

**Model count:** 15 models · **Test count:** 44 passing · **Materialization:** staging + intermediate as `view`, marts as `table`

---

## Dashboard Pages

| Page | What it shows |
|---|---|
| **Overview** | Platform-wide KPIs — GMV, orders, customers, sellers, payment mix, review distribution |
| **Revenue** | Monthly GMV trend, order volume, top 10 categories, revenue by state, cancellation rate, payment GMV |
| **Customers** | Segment mix (one-time / repeat / loyal), LTV distribution, AOV by segment, orders vs LTV scatter |
| **Sellers** | Health score distribution, review score vs GMV bubble chart, top 20 sellers by revenue |
| **Delivery** | Monthly on-time rate vs 80% SLA target, avg days to deliver, on-time rate by state |

---

## Data Quality Challenges

Building this pipeline on real-world data surfaced six data quality issues, each fixed in the appropriate dbt layer:

| # | Issue | Layer | Fix |
|---|-------|-------|-----|
| 1 | 789 duplicate review IDs — customers could edit reviews post-delivery | `stg_reviews` | `ROW_NUMBER()` deduplication keeping most recent review |
| 2 | 775 orders with no items — canceled/abandoned orders missing from order_items | `int_orders_enriched` | `COALESCE(..., 0)` to preserve orders without hiding cancellations |
| 3 | 122 customers with duplicate LTV rows — same person, multiple delivery cities | `int_customer_orders` | Removed city/state from `GROUP BY`, group by `customer_unique_id` only |
| 4 | Misspelled column names in source — `product_name_lenght` (typo) | `stg_products` | Renamed with alias in staging so all downstream models use correct names |
| 5 | NULL on-time delivery rate for 9 state/month combos with zero deliveries | `mart_delivery` | `NULLIF` + `COALESCE` to handle zero-denominator division safely |
| 6 | All product categories in Portuguese — unusable for English dashboards | `stg_products` → marts | Joined translation table with `COALESCE` fallback chain |

> All issues were caught by dbt's built-in `not_null` and `unique` tests before any data reached the dashboard — demonstrating the value of testing at every layer.

---

## Key Business Insights

- **R$20.3M GMV** generated across 100K orders, peaking at **R$1.58M in Nov 2017** (Black Friday)
- **96.9% of customers are one-time buyers** — retention is the single largest growth opportunity
- **Credit card accounts for ~74% of GMV**; boleto (bank slip) serves Brazil's unbanked segment
- **Seller health score** composite metric: review rating (40%) + on-time delivery rate (40%) + order volume (20%) — flags at-risk sellers before they damage platform reputation
- Several states fall **below the 80% on-time SLA target** — identified as priority logistics problem areas

---

## How to Run Locally

**Prerequisites:** Python 3.11+, a [MotherDuck](https://motherduck.com/) account with the Olist dataset loaded, and a MotherDuck token.

### 1. Clone the repo
```bash
git clone https://github.com/krutispatil/dbt_analytics.git
cd dbt_analytics
```

### 2. Set up dbt
```bash
pip install dbt-duckdb==1.10.1

# Create ~/.dbt/profiles.yml with:
# my_pipeline:
#   target: dev
#   outputs:
#     dev:
#       type: duckdb
#       path: "md:olist?motherduck_token={{ env_var('MOTHERDUCK_TOKEN') }}"
#       schema: dbt_kpatil
#       threads: 4

export MOTHERDUCK_TOKEN=your_token_here
cd my_pipeline
dbt run
dbt test
```

### 3. Run the dashboard
```bash
cd ../dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open `http://localhost:8501`

---

## Live Dashboard

**→ https://dbtanalytics-n9yv9r9bmfkqodl2reemnk.streamlit.app/**

---

*Built by [Kruti Spatil](https://github.com/krutispatil) · Data sourced from [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)*
