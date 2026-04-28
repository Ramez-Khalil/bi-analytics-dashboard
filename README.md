# BI Analytics Dashboard

A Python and SQL-powered business intelligence dashboard for aggregating, analyzing, and visualizing key performance indicators (KPIs) from relational data sources.

---

## Overview

This project demonstrates an end-to-end business intelligence pipeline — from raw relational data through SQL-based transformation to an interactive Python dashboard. It is designed to surface actionable insights across sales, operations, and customer metrics.

---

## Features

- **SQL Data Layer** — Optimized queries and views for KPI aggregation across multiple fact and dimension tables
- **ETL Pipeline** — Python-driven extract, transform, load workflow to ingest and clean raw data
- **Interactive Visualizations** — Line charts, bar graphs, heatmaps, and summary tables for trend analysis
- **KPI Tracking** — Pre-built metrics including revenue, churn rate, customer lifetime value, and fulfillment time
- **Multi-Source Support** — Connects to MySQL, PostgreSQL, and SQLite databases via a unified connector
- **Scheduled Refresh** — Configurable data refresh intervals using Python scheduling
- **Export to PDF/CSV** — Dashboard snapshots and raw data exports for stakeholder reporting

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Database | MySQL / PostgreSQL / SQLite |
| Data Processing | `pandas`, `numpy` |
| Visualization | `matplotlib`, `seaborn`, `plotly` |
| Database Connector | `SQLAlchemy`, `psycopg2`, `mysql-connector-python` |
| Dashboard UI | `Dash` (Plotly) |
| Scheduling | `APScheduler` |

---

## Installation

```bash
git clone https://github.com/Ramez-Khalil/bi-analytics-dashboard.git
cd bi-analytics-dashboard
pip install -r requirements.txt
```

Configure your database connection in `config/db_config.yaml`:

```yaml
database:
  engine: postgresql
  host: localhost
  port: 5432
  name: analytics_db
  user: your_user
  password: your_password
```

---

## Usage

```bash
# Run the full ETL pipeline and launch dashboard
python main.py

# Run ETL only (no dashboard)
python etl/pipeline.py

# Launch dashboard against existing data
python dashboard/app.py
```

The dashboard will be available at `http://localhost:8050`.

---

## Database Schema

The underlying schema follows a star schema design:

```
fact_sales
├── dim_customer
├── dim_product
├── dim_date
└── dim_region
```

Key SQL views pre-computed for dashboard performance:
- `vw_monthly_revenue` — Monthly revenue aggregated by region and product category
- `vw_customer_retention` — Cohort-based retention and churn rates
- `vw_top_products` — Top-performing SKUs by revenue and units sold

---

## Project Structure

```
bi-analytics-dashboard/
├── config/
│   └── db_config.yaml       # Database connection settings
├── etl/
│   ├── extract.py           # Data extraction from source DB
│   ├── transform.py         # Cleaning and business logic
│   └── load.py              # Load into analytics schema
├── sql/
│   ├── schema.sql           # Table definitions
│   ├── views.sql            # KPI views
│   └── queries/             # Named analytical queries
├── dashboard/
│   ├── app.py               # Dash app entry point
│   ├── layouts.py           # Page layouts
│   └── charts.py            # Chart components
├── requirements.txt
└── README.md
```

---

## Sample KPIs

| Metric | Description |
|--------|-------------|
| Monthly Recurring Revenue | Total revenue aggregated by month |
| Customer Churn Rate | % of customers lost in a given period |
| Average Order Value | Mean transaction value by segment |
| Fulfillment SLA Compliance | % of orders delivered within SLA window |
| Top 10 Products by Revenue | Ranked product performance |

---

## Skills Demonstrated

- Relational database design (star schema, normalization)
- SQL query optimization, window functions, and aggregation
- Python data engineering with pandas and SQLAlchemy
- Interactive dashboard development with Plotly Dash
- ETL pipeline architecture

---

*Developed as a capstone analytics project at Cal Poly Pomona.*
