# NutriBox Power BI 3-Page Dashboard Layout Specification
**Project:** Founder's Office Dashboard  
**Screen Canvas:** 16:9 Widescreen (1920 × 1080 px)  
**Layout Grid:** 8px baseline grid, 16px page margins, 12px visual gap  
**Target Audience:** Founder, Co-founders, VP Growth, Operations Lead

---

## 1. Brand Design System & Color Palette

| Token Name | Hex Code | Semantic Role |
| :--- | :---: | :--- |
| **Primary Navy** | `#1E293B` | Titles, card text, primary headers, major visual bars |
| **Accent Blue** | `#0284C7` | Key revenue lines, selected slicer items, interactive highlights |
| **Success Emerald**| `#10B981` | Positive WoW growth, ROAS $\ge 2.5\text{x}$, healthy runway $\ge 9\text{ mos}$ |
| **Alert Crimson** | `#EF4444` | Negative WoW indicators, refund spikes $> 5\%$, poor ROAS $< 1.0\text{x}$ |
| **Neutral Surface**| `#F8FAFC` | Card container background, table alternate row shading |
| **Border Slate** | `#CBD5E1` | Card container border (1px solid, 6px border radius) |

* **Typography:** Segoe UI / Segoe UI Semibold
* **Card Container Styling:** Fill: `#F8FAFC`, Border: `#CBD5E1` (1px), Shadow: None, Header Band: 3px solid `#0284C7`.

---

## 2. Global Slicer Header Bar (Consistent Across Pages 1, 2 & 3)

* **Location:** Top Banner (`X: 16px`, `Y: 16px`, `W: 1888px`, `H: 80px`)
* **Background Fill:** `#1E293B`

| Control Element | Power BI Visual Type | Source Field | Visual Settings |
| :--- | :--- | :--- | :--- |
| **Report Title** | Text Box | Static | Font: Segoe UI Bold 20pt `#FFFFFF`, "NUTRIBOX FOUNDER'S OFFICE" |
| **Subtitle** | Text Box | Static | Font: Segoe UI Regular 10pt `#94A3B8`, "Weekly Performance & Strategic Intelligence" |
| **Slicer 1 (Date)** | Slicer (Dropdown) | `'Dim_Date'[week]` | Single select toggle or multi-select with search. Default: `W52` |
| **Slicer 2 (Channel)**| Slicer (Dropdown) | `'Fact_Orders'[channel]` | Multi-select with "Select All" |
| **Slicer 3 (Product)**| Slicer (Dropdown) | `'Fact_Orders'[product]` | Multi-select with "Select All" |
| **Slicer 4 (City)** | Slicer (Dropdown) | `'Dim_Customer'[city]` | Multi-select with "Select All" |

---

## 3. Page 1: Executive Summary
**Primary Question Answered:** *"How is the business performing this week?"*

### 3.1 KPI Cards Row (`Y: 110px`, `H: 130px`)
6 KPI Cards across the canvas width (`W: 300px` each, `Gap: 14px`):

1. **Delivered Revenue (W52):**
   - Value: `[Delivered Revenue]` (Format: `₹#,##0`)
   - Subtitle: `[Revenue WoW KPI Icon]` (Green if positive, Red if negative)
2. **Monthly Recurring Revenue (MRR):**
   - Value: `[MRR]` (Format: `₹#,##0`)
   - Subtitle: `[MRR WoW %]` with green/red dynamic text
3. **Active Subscribers:**
   - Value: `[Active Customers]` (Format: `#,##0`)
   - Subtitle: `[Total Orders]` placed this week
4. **Gross Margin %:**
   - Value: `[Gross Margin %]` (Format: `0.00%`)
   - Target line: Benchmark $50.0\%$
5. **Blended CAC:**
   - Value: `[CAC]` (Format: `₹#,##0`)
   - Subtitle: `[CAC WoW %]` (Inverted: Red if increased, Green if reduced)
6. **Cash Runway (Months):**
   - Value: `[Runway (Months)]` (Format: `0.0 "Months"`)
   - Subtitle: Cash Balance `[Latest Cash Balance]`

### 3.2 Visuals Grid (`Y: 260px`, `H: 790px`)

* **Visual 1 (Top Left): Weekly Delivered Revenue Trajectory**
  - **Visual:** Line Chart (`X: 16px`, `Y: 260px`, `W: 930px`, `H: 380px`)
  - **X-axis:** `'Dim_Date'[week]`
  - **Y-axis:** `[Delivered Revenue]`, `[Delivered Revenue PW]` (Dotted line for prior week comparison)
  - **Color:** Accent Blue (`#0284C7`), prior week Slate (`#94A3B8`)
  - **Title:** "Weekly Recognized Revenue vs Prior Week (52-Week Trend)"

* **Visual 2 (Top Right): Channel Revenue & ROAS Matrix**
  - **Visual:** Clustered Column & Line Chart (`X: 960px`, `Y: 260px`, `W: 944px`, `H: 380px`)
  - **X-axis:** `'Fact_Marketing'[channel]`
  - **Column Y-axis:** `[Marketing Spend]` (`#1E293B`), `[Ad Revenue]` (`#0284C7`)
  - **Line Y-axis:** `[ROAS]` (`#10B981`)
  - **Reference Line:** Constant line on Line axis at $2.50\text{x}$

* **Visual 3 (Bottom Left): Attributed Delivered Revenue Share by Channel**
  - **Visual:** Donut Chart (`X: 16px`, `Y: 660px`, `W: 460px`, `H: 390px`)
  - **Legend:** `'Fact_Orders'[channel]`
  - **Values:** `[Delivered Revenue]`
  - **Data Labels:** Percentage and Category Name

* **Visual 4 (Bottom Center): Unit Economics Health: LTV vs CAC**
  - **Visual:** Clustered Bar Chart (`X: 490px`, `Y: 660px`, `W: 456px`, `H: 390px`)
  - **Y-axis:** `'Dim_Customer'[acquisition_channel]`
  - **X-axis:** `[CAC]` vs `[LTV]`
  - **Target:** Annotate $3.0\text{x}$ benchmark ratio

* **Visual 5 (Bottom Right): Monthly Cash Balance & Net Burn Run-Rate**
  - **Visual:** Area Chart (`X: 960px`, `Y: 660px`, `W: 944px`, `H: 390px`)
  - **X-axis:** `'Fact_Finance'[month]`
  - **Y-axis:** `[Latest Cash Balance]`
  - **Secondary Line:** `[Monthly Net Profit]`
  - **Shading:** Gradient Navy to White

---

## 4. Page 2: Growth & Marketing
**Primary Question Answered:** *"Where are our acquisition dollars going, and which channels are working?"*

### 4.1 Marketing KPI Ribbon (`Y: 110px`, `H: 110px`)
5 Cards (`W: 360px` each):
1. **Total Marketing Spend:** `[Marketing Spend]`
2. **Total Storefront Impressions:** `[Ad Impressions]`
3. **Total Storefront Clicks:** `[Ad Clicks]` (with `[CTR %]`)
4. **Storefront Conversions:** `[Storefront Conversions]` (with `[CVR %]`)
5. **Blended ROAS:** `[ROAS]` (Dynamic color: Green if $>2.0\text{x}$, Red if $<1.0\text{x}$)

### 4.2 Visuals Grid (`Y: 240px`, `H: 810px`)

* **Visual 1 (Top Left): Full-Funnel Conversion Drop-off**
  - **Visual:** Funnel Visual (`X: 16px`, `Y: 240px`, `W: 550px`, `H: 400px`)
  - **Stages:** Impressions $\to$ Clicks $\to$ Conversions $\to$ Delivered Orders
  - **Values:** `[Ad Impressions]`, `[Ad Clicks]`, `[Storefront Conversions]`, `[Delivered Orders]`
  - **Data Labels:** Stage-to-stage percentage retention

* **Visual 2 (Top Right): Channel Unit Economics (CAC, CPC, CVR)**
  - **Visual:** Table with Data Bars (`X: 580px`, `Y: 240px`, `W: 1324px`, `H: 400px`)
  - **Columns:**
    - Channel
    - Marketing Spend (`₹#,##0`)
    - New Customers (`#,##0`)
    - CAC (`₹#,##0` with background gradient: Green low, Red high)
    - Clicks (`#,##0`)
    - CTR % (`0.00%`)
    - CPC (`₹0.00`)
    - CVR % (`0.00%`)
    - ROAS (`0.00x` with conditional text icon)

* **Visual 3 (Bottom Left): Weekly Marketing Spend Allocation by Channel**
  - **Visual:** 100% Stacked Area Chart (`X: 16px`, `Y: 660px`, `W: 930px`, `H: 390px`)
  - **X-axis:** `'Dim_Date'[week]`
  - **Y-axis:** `[Marketing Spend]`
  - **Legend:** `'Fact_Marketing'[channel]`
  - **Observation Highlight:** Reveals disproportionate Instagram budget drain

* **Visual 4 (Bottom Right): Customer Acquisition by Metro City & Subscription Plan**
  - **Visual:** Matrix Visual (`X: 960px`, `Y: 660px`, `W: 944px`, `H: 390px`)
  - **Rows:** `'Dim_Customer'[city]`
  - **Columns:** `'Dim_Customer'[plan]`
  - **Values:** `[New Signups]`, `[Delivered Revenue]`
  - **Heatmap:** Color scale on Delivered Revenue

---

## 5. Page 3: Operations & Customer Health
**Primary Question Answered:** *"Are our customers happy, delivered on time, and retaining?"*

### 5.1 Operations KPI Ribbon (`Y: 110px`, `H: 110px`)
5 Cards (`W: 360px` each):
1. **Pending Fulfillment Orders:** `[Pending Orders]`
2. **Average Delivery Time:** `[Avg Delivery Days]` (Target $< 4.0\text{ days}$)
3. **Refund Rate %:** `[Refund Rate %]` (Alert if $> 3.0\%$)
4. **Customer Satisfaction (CSAT):** `[CSAT Score]` (Scale 1-5, Benchmark $\ge 4.2$)
5. **Net Promoter Score (NPS):** `[NPS Score]` (Benchmark $> +50$)

### 5.2 Visuals Grid (`Y: 240px`, `H: 810px`)

* **Visual 1 (Top Left): Product-Level Refund Spike Detector (Week 46 Quality Incident)**
  - **Visual:** Line Chart (`X: 16px`, `Y: 240px`, `W: 1100px`, `H: 400px`)
  - **X-axis:** `'Dim_Date'[week]`
  - **Y-axis:** `[Refund Rate %]`
  - **Legend:** `'Fact_Orders'[product]`
  - **Visual Marker:** Anomaly flag on Week 46 for *"Keto Seeds Delight"* showing refund rate jumping to $>25\%$ due to packaging seal defect.

* **Visual 2 (Top Right): NPS Sentiment Breakdown (Promoters vs Detractors)**
  - **Visual:** 100% Stacked Bar Chart (`X: 1130px`, `Y: 240px`, `W: 774px`, `H: 400px`)
  - **Y-axis:** `'Dim_Date'[week]`
  - **X-axis:** Count of feedback
  - **Legend:** Sentiment Bucket (Promoters: `#10B981`, Passives: `#94A3B8`, Detractors: `#EF4444`)

* **Visual 3 (Bottom Left): Delivery SLA Performance by Destination City**
  - **Visual:** Clustered Bar Chart (`X: 16px`, `Y: 660px`, `W: 650px`, `H: 390px`)
  - **Y-axis:** `'Dim_Customer'[city]`
  - **X-axis:** `[Avg Delivery Days]`
  - **Threshold Line:** SLA Target at 4.0 days

* **Visual 4 (Bottom Right): SKU Performance & Defect Audit Matrix**
  - **Visual:** Table (`X: 680px`, `Y: 660px`, `W: 1224px`, `H: 390px`)
  - **Columns:**
    - Product SKU
    - Total Orders Placed
    - Delivered Revenue (`₹#,##0`)
    - Refunded Units
    - Refund Rate % (Conditional Formatting: Red if $> 4.0\%$)
    - Average CSAT (Conditional Formatting: Red if $< 4.0$)
    - COGS Contribution %

---

## 6. Conditional Formatting Business Rules

1. **WoW Indicators:**
   - If Metric is Growth-oriented (Revenue, MRR, Active Subs, Orders):
     - $\Delta \ge 0\% \implies$ `#10B981` (Green)
     - $\Delta < 0\% \implies$ `#EF4444` (Red)
   - If Metric is Cost/Friction-oriented (CAC, Burn Rate, Refund %, Delivery Days):
     - $\Delta \le 0\% \implies$ `#10B981` (Green - favorable reduction)
     - $\Delta > 0\% \implies$ `#EF4444` (Red - unfavorable increase)

2. **ROAS Color Thresholds:**
   - $\text{ROAS} \ge 2.50\text{x} \implies$ Deep Emerald (`#059669`)
   - $1.50\text{x} \le \text{ROAS} < 2.50\text{x} \implies$ Amber Slate (`#D97706`)
   - $\text{ROAS} < 1.50\text{x} \implies$ Crimson Alert (`#DC2626`) [Flags Instagram at 0.79x]

3. **Product Quality Alert:**
   - If `Refund Rate %` $> 5.0\% \implies$ Cell Background fills with Soft Red (`#FEE2E2`) and text Crimson (`#991B1B`).
