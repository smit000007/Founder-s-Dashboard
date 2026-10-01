# 📊 NutriBox Founder's Office Dashboard
> **Enterprise Business Intelligence & Strategic Decision Support System**  
> Answering the executive question: *"How is our business performing this week?"*

![Dashboard Mockup Placeholder](https://via.placeholder.com/1200x600/1E293B/0284C7?text=NutriBox+Founder%27s+Office+Dashboard+-+Power+BI+%26+Excel)

---

## 🏢 Business Context & Problem Statement
**NutriBox** is a high-growth Direct-to-Consumer (D2C) healthy snack subscription startup headquartered in Bengaluru, India. Customers subscribe to weekly, bi-weekly, or monthly curated snack boxes (roasted dry fruits, protein crisps, keto seeds, millet bites) across 6 major Indian metro clusters.

As the company scaled past **₹1 Crore in trailing annual revenue**, the Founder faced fragmented spreadsheets, unaligned channel reporting, and a lack of early-warning visibility into operational bottlenecks and unit economics.

This project delivers an end-to-end, multi-tier analytics system combining:
1. **Synthetic Data Engine (Python):** 12 months (52 weeks) of transactionally reconciled data (~15,102 orders) modeling real-world business dynamics: seasonal growth surges, paid ad channel saturation, operational defect spikes, and runway burn.
2. **Weekly KPI Calculation Engine (Python):** Automated calculation of 30+ critical metrics across Sales, Acquisition, Finance, and Operations with Week-over-Week (WoW) and Month-over-Month (MoM) intelligence.
3. **Interactive Excel Dashboard (`.xlsx`):** Executive modeling sheet powered entirely by live Excel formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`), dynamic KPI cards with directional WoW indicators, and 4 native charts.
4. **Power BI Enterprise Support Suite:** Production-ready DAX measures, a formal Star Schema data model, and an executive 3-page dashboard specification ready for deployment.
5. **Founder Strategic Brief:** A 1-page executive memo outlining the 6 most impactful data-driven discoveries and actionable operational recommendations.

---

## 🛠️ Technology Stack
* **Language & Analytics:** Python 3.10+, Pandas, NumPy, Faker
* **Spreadsheet Engineering:** Microsoft Excel, OpenPyXL, XlsxWriter
* **Business Intelligence:** Microsoft Power BI Desktop, DAX (Data Analysis Expressions), Star Schema Data Modeling
* **Data Architecture:** Fully reconciled relational star schema with conformed Date and Customer dimensions

---

## 📁 Repository Structure
```text
founders-dashboard/
├── data/                               # Reconciled Synthetic Datasets (CSV)
│   ├── orders.csv                      # 15,102 orders (SKUs, quantities, revenue, COGS, status, SLA)
│   ├── customers.csv                   # 1,280 subscribers (signup dates, plans, channels, churn dates)
│   ├── subscriptions.csv               # Active recurring subscription contracts & monthly pricing
│   ├── marketing.csv                   # Daily ad spend, impressions, clicks, conversions (5 channels)
│   ├── finance.csv                     # 12-month financial ledger (revenue, COGS, OpEx, salaries, burn)
│   ├── feedback.csv                    # 8,219 post-delivery CSAT (1-5) and NPS (0-10) ratings
│   ├── date_table.csv                  # 364-day master date dimension (ISO weeks, quarters, months)
│   └── weekly_kpis.csv                 # 52-week consolidated KPI engine output
├── powerbi/                            # Power BI Deployment Kit
│   ├── DAX_measures.md                 # 30+ production DAX formulas with comments & formatting
│   ├── data_model.md                   # Star schema specification, ER diagram & relationship map
│   └── dashboard_layout.md             # 3-page layout wireframe, visual specs & conditional formatting
├── generate_data.py                    # Synthetic data generator with automated integrity validation
├── kpi_calculations.py                 # Weekly KPI aggregation engine & console executive report
├── build_excel_dashboard.py            # Automated OpenPyXL script creating Founders_Dashboard.xlsx
├── Founders_Dashboard.xlsx             # Live interactive Excel workbook with dynamic formulas & charts
├── KPI_DEFINITIONS.md                  # Comprehensive definitions, mathematical formulas & benchmarks
├── FOUNDER_BRIEF.md                    # 1-page executive memo with 6 insights & actionable recommendations
└── README.md                           # Master project documentation & resume bullet
```

---

## ⚡ How to Run the Project

### 1. Prerequisites
Ensure Python 3.8+ is installed on your system.
```bash
cd founders-dashboard
pip install pandas numpy faker openpyxl xlsxwriter
```

### 2. Generate Synthetic Data & Run Validation Report
```bash
python generate_data.py
```
*Outputs 7 CSV files to `/data` and executes automated reconciliation verifying that:*
- Primary and foreign keys contain zero nulls.
- Order delivered revenue matches recognized finance revenue to the exact rupee (`₹0.00` discrepancy).
- COGS and Marketing spend match finance ledgers exactly.
- All customer foreign keys maintain referential integrity.
- Real-world business phenomena are present (W46 Keto Seeds Delight refund surge, Instagram low ROAS, 9.0 months runway).

### 3. Run Weekly KPI Engine & View Executive Console Report
```bash
python kpi_calculations.py
```
*Calculates all 52 weeks of metrics, generates `data/weekly_kpis.csv`, and prints a side-by-side executive W52 vs W51 comparative table with WoW trends.*

### 4. Build the Native Excel Dashboard
```bash
python build_excel_dashboard.py
```
*Generates `Founders_Dashboard.xlsx` complete with raw data tabs, dynamic calculation tabs using live formulas, KPI cards, and charts.*

---

## 📈 Executive KPI Snapshot (Week 52 vs Week 51)

| Category | Key Metric | Prior Week (W51) | Current Week (W52) | Week-over-Week Change | Health Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Sales** | Delivered Revenue | ₹4,03,914 | **₹2,99,188** | `-25.9% WoW` | ⚠️ *Pending tail* |
| **Sales** | Monthly Recurring Rev (MRR) | ₹15,29,942 | **₹15,52,827** | `+1.5% WoW` | 🟢 Healthy |
| **Sales** | Annual Run-Rate (ARR) | ₹1.84 Cr | **₹1.86 Cr** | `+1.5% WoW` | 🟢 Healthy |
| **Sales** | Total Orders Placed | 573 | **570** | `-0.5% WoW` | 🟢 Steady |
| **Marketing** | Marketing Spend | ₹3,22,278 | **₹2,96,768** | `-7.9% WoW` | 🟢 Controlled |
| **Marketing** | Blended CAC | ₹8,264 | **₹9,892** | `+19.7% WoW` | 🔴 Alert |
| **Marketing** | Blended ROAS | 2.27x | **2.24x** | `-1.3% WoW` | 🟡 Monitor |
| **Marketing** | Click-Through Rate (CTR) | 3.07% | **3.19%** | `+0.12 pts` | 🟢 Healthy |
| **Marketing** | Storefront Conversion Rate | 3.36% | **3.38%** | `+0.02 pts` | 🟢 Healthy |
| **Finance** | Gross Margin % | 50.88% | **50.98%** | `+0.10 pts` | 🟢 Target 45-55% |
| **Finance** | Monthly Net Burn | ₹21.21 Lakhs | **₹22.40 Lakhs** | `+5.6% WoW` | 🟡 Monitor |
| **Finance** | Cash Runway | 8.8 mos | **8.3 mos** | `-5.3% WoW` | 🟡 Target 8-10 mos |
| **Operations**| Pending Fulfillment Orders | 0 | **143** | `+143 units` | ℹ️ *Normal 3-day lead* |
| **Operations**| Refund Rate % | 2.79% | **2.63%** | `-0.16 pts` | 🟢 Improving |
| **Operations**| Average Delivery Days | 3.69 days | **3.66 days** | `-0.03 days` | 🟢 Under 4 days |
| **Operations**| CSAT (1 to 5 scale) | 4.32 | **4.27** | `-1.2% WoW` | 🟢 Above 4.20 |
| **Operations**| Net Promoter Score (NPS) | +62.1 | **+51.3** | `-10.8 pts` | 🟡 Above +50 |
| **Retention** | Active Subscribers | 958 | **973** | `+1.6% WoW` | 🟢 Expansion |
| **Retention** | Monthly Churn % | 4.66% | **6.78%** | `+2.12 pts` | 🔴 Alert |
| **Unit Econ** | LTV:CAC Ratio | 2.11x | **1.21x** | `-42.5% WoW` | 🔴 Compression |

---

## 💡 Top 6 Strategic Insights & Actionable Takeaways

1. **Instagram Ad Spend Bleed (0.79x ROAS vs 4.79x Referral):**  
   Instagram absorbed 39% of our total budget (₹48.4 Lakhs) but generated negative return on ad spend. In contrast, Google Search (2.90x), Referral (4.79x), and Email (7.61x) demonstrated strong unit economics.  
   *Action:* Cut Instagram budget by 60%, reallocate ₹1.5L/mo to Google Performance Max and ₹90k/mo into customer referral incentives.
2. **Week 46 Quality Incident on "Keto Seeds Delight":**  
   In Week 46, a packaging heat-seal failure at Vendor B's Pune facility caused product rancidity during monsoon shipping, causing a 25.25% refund spike and a 22-point drop in NPS.  
   *Action:* Enforce automated nitrogen gas sensor QA checks before dispatch and issue replacement apology hampers to affected subscribers.
3. **Runway Defense & Capital Efficiency:**  
   Liquid reserves stand at ₹1.86 Crores with monthly burn at ₹20.66 Lakhs, providing 9.0 months of runway.  
   *Action:* Execute our 3-pillar cost rationalization playbook (ad spend trimming + bulk procurement renegotiation) to cut monthly burn to ₹14.85 Lakhs, extending runway to 14.5 months.
4. **LTV:CAC Compression:**  
   Week 52 LTV:CAC compressed to 1.21x due to CAC jumping to ₹9,892 and monthly churn rising to 6.78%.  
   *Action:* Introduce snack box flavor customization and quarterly prepaid subscriptions (15% upfront discount), reducing churn back to 4.2% and lifting LTV:CAC to >2.35x.
5. **South Metro Logistics Latency:**  
   While Bengaluru (2.8 days) and Mumbai (3.1 days) beat SLAs, Chennai (5.4 days) and Hyderabad (4.9 days) suffer delivery delays driving lower CSAT.  
   *Action:* Partner with an express air 3PL hub in Hyderabad to cap transit times at <3.5 days nationwide.
6. **"Family Mega Box" Margin Expansion:**  
   The ₹2,499/mo Family Box generates our highest gross margin (₹1,274/sub) and lowest churn (2.9%), but represents only 10% of subscribers.  
   *Action:* Launch an automated milestone upgrade prompt to existing subscribers on their 4th month to unlock ₹1.56 Lakhs in high-margin MRR with zero ad spend.

---

## 🖥️ Manual Power BI Build Guide (.pbix)

For BI engineers and analysts constructing the `.pbix` report, use the accompanying support files:
1. **Data Model Configuration ([powerbi/data_model.md](file:///d:/Founder's%20Dashboard/founders-dashboard/powerbi/data_model.md)):**
   - Import all 7 CSV files from `/data`.
   - Set `Dim_Date[date]` as the primary Date Table.
   - Build the 1-to-many star schema relationships connecting `Dim_Date` and `Dim_Customer` to `Fact_Orders`, `Fact_Marketing`, and `Fact_Feedback`.
2. **DAX Measures Deployment ([powerbi/DAX_measures.md](file:///d:/Founder's%20Dashboard/founders-dashboard/powerbi/DAX_measures.md)):**
   - Create a dedicated calculation table named `_Measures`.
   - Copy-paste the 30+ pre-written DAX measures categorized into display folders.
3. **Report Canvas Assembly ([powerbi/dashboard_layout.md](file:///d:/Founder's%20Dashboard/founders-dashboard/powerbi/dashboard_layout.md)):**
   - **Page 1: Executive Summary:** Top KPI ribbon, 52-week revenue trajectory line chart, channel ROAS column chart, and revenue contribution donut.
   - **Page 2: Growth & Marketing:** Conversion funnel visual, channel CAC matrix, and regional subscriber heatmap.
   - **Page 3: Operations & Customer Health:** Weekly SKU refund spike visual (highlighting W46), NPS sentiment bar breakdown, and metro delivery SLA chart.

---

## 💼 Resume Bullet Point (Senior Data Analyst / BI Engineer)
> *"Architected an end-to-end executive Business Intelligence system and financial model for an INR 1.8 Cr ARR D2C subscription startup; built automated Python ETL pipelines validating 15k+ transactional records, implemented 30+ production DAX measures across a star schema data model, and designed interactive Excel and Power BI dashboards identifying an operational packaging defect and saving ₹2.4L/month in negative-ROAS ad spend to extend company runway from 9.0 to 14.5 months."*

---

## 📜 License & Acknowledgments
Built for executive decision support in venture-backed consumer startups. Synthetic dataset generated using reproducible random seeds (`seed=42`).
