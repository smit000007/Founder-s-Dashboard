# NutriBox Power BI DAX Measures Repository
**Project:** Founder's Office Dashboard  
**Business Model:** D2C Subscription Healthy Snacks (India, INR)  
**Standard Date Table Reference:** `'Dim_Date'[date]`, `'Dim_Date'[week]`

---

## Structure & Implementation Note
For clean Power BI data model maintenance, create an empty dedicated calculation table named `_Measures` and house these measures under designated display folders.

---

## 1. Sales & Recurring Revenue Measures

### [Delivered Revenue]
```dax
Delivered Revenue = 
CALCULATE(
    SUM('Fact_Orders'[revenue]),
    'Fact_Orders'[status] = "Delivered"
)
```
* **Description:** Gross recognized revenue from successfully delivered snack orders.
* **Format:** `₹#,##0`

### [Gross Revenue (All Statuses)]
```dax
Gross Revenue = 
SUM('Fact_Orders'[revenue])
```
* **Format:** `₹#,##0`

### [Total Orders Placed]
```dax
Total Orders = 
COUNTROWS('Fact_Orders')
```
* **Format:** `#,##0`

### [Delivered Orders Count]
```dax
Delivered Orders = 
CALCULATE(
    COUNTROWS('Fact_Orders'),
    'Fact_Orders'[status] = "Delivered"
)
```
* **Format:** `#,##0`

### [Pending Orders Count]
```dax
Pending Orders = 
CALCULATE(
    COUNTROWS('Fact_Orders'),
    'Fact_Orders'[status] = "Pending"
)
```
* **Format:** `#,##0`

### [Refunded Orders Count]
```dax
Refunded Orders = 
CALCULATE(
    COUNTROWS('Fact_Orders'),
    'Fact_Orders'[status] = "Refunded"
)
```
* **Format:** `#,##0`

### [Average Order Value (AOV)]
```dax
AOV = 
DIVIDE(
    [Delivered Revenue],
    [Delivered Orders],
    0
)
```
* **Format:** `₹#,##0.00`

### [Active Customers Count]
```dax
Active Customers = 
VAR CurrentDate = MAX('Dim_Date'[date])
RETURN
CALCULATE(
    DISTINCTCOUNT('Dim_Customer'[customer_id]),
    'Dim_Customer'[signup_date] <= CurrentDate,
    ISBLANK('Dim_Customer'[churn_date]) || 'Dim_Customer'[churn_date] > CurrentDate,
    ALL('Dim_Date')
)
```
* **Description:** Total unique paying subscribers who have signed up and have not churned as of the current filter context date.
* **Format:** `#,##0`

### [New Signups]
```dax
New Signups = 
CALCULATE(
    DISTINCTCOUNT('Dim_Customer'[customer_id]),
    USERELATIONSHIP('Dim_Customer'[signup_date], 'Dim_Date'[date])
)
```
* **Format:** `#,##0`

### [Monthly Recurring Revenue (MRR)]
```dax
MRR = 
VAR CurrentDate = MAX('Dim_Date'[date])
VAR ActiveCustomerList = 
    CALCULATETABLE(
        VALUES('Dim_Customer'[customer_id]),
        'Dim_Customer'[signup_date] <= CurrentDate,
        ISBLANK('Dim_Customer'[churn_date]) || 'Dim_Customer'[churn_date] > CurrentDate,
        ALL('Dim_Date')
    )
RETURN
CALCULATE(
    SUM('Dim_Subscription'[monthly_price]),
    TREATAS(ActiveCustomerList, 'Dim_Subscription'[customer_id])
)
```
* **Description:** Monthly contracted subscription value across all currently active subscribers.
* **Format:** `₹#,##0`

### [Annual Recurring Revenue (ARR)]
```dax
ARR = 
[MRR] * 12
```
* **Format:** `₹#,##0`

---

## 2. Marketing & Acquisition Measures

### [Marketing Spend]
```dax
Marketing Spend = 
SUM('Fact_Marketing'[spend])
```
* **Format:** `₹#,##0`

### [Ad Impressions]
```dax
Ad Impressions = 
SUM('Fact_Marketing'[impressions])
```
* **Format:** `#,##0`

### [Ad Clicks]
```dax
Ad Clicks = 
SUM('Fact_Marketing'[clicks])
```
* **Format:** `#,##0`

### [Storefront Conversions]
```dax
Storefront Conversions = 
SUM('Fact_Marketing'[conversions])
```
* **Format:** `#,##0`

### [Ad-Attributed Revenue]
```dax
Ad Revenue = 
SUM('Fact_Marketing'[ad_revenue])
```
* **Format:** `₹#,##0`

### [Click-Through Rate (CTR)]
```dax
CTR % = 
DIVIDE(
    [Ad Clicks],
    [Ad Impressions],
    0
)
```
* **Format:** `0.00%`

### [Cost Per Click (CPC)]
```dax
CPC = 
DIVIDE(
    [Marketing Spend],
    [Ad Clicks],
    0
)
```
* **Format:** `₹#,##0.00`

### [Conversion Rate (CVR %)]
```dax
CVR % = 
DIVIDE(
    [Storefront Conversions],
    [Ad Clicks],
    0
)
```
* **Format:** `0.00%`

### [Blended CAC]
```dax
CAC = 
DIVIDE(
    [Marketing Spend],
    [New Signups],
    BLANK()
)
```
* **Description:** Marketing spend required to acquire one newly registered customer.
* **Format:** `₹#,##0`

### [Return on Ad Spend (ROAS)]
```dax
ROAS = 
DIVIDE(
    [Ad Revenue],
    [Marketing Spend],
    0
)
```
* **Format:** `0.00x`

---

## 3. Financial Health & Runway Measures

### [Total COGS]
```dax
COGS = 
CALCULATE(
    SUM('Fact_Orders'[cogs]),
    'Fact_Orders'[status] = "Delivered"
)
```
* **Format:** `₹#,##0`

### [Gross Profit]
```dax
Gross Profit = 
[Delivered Revenue] - [COGS]
```
* **Format:** `₹#,##0`

### [Gross Margin %]
```dax
Gross Margin % = 
DIVIDE(
    [Gross Profit],
    [Delivered Revenue],
    0
)
```
* **Format:** `0.00%`

### [Latest Cash Balance]
```dax
Latest Cash Balance = 
CALCULATE(
    LASTNONBLANKVALUE('Dim_Date'[date], SUM('Fact_Finance'[cash_balance])),
    ALL('Dim_Date')
)
```
* **Format:** `₹#,##0`

### [Monthly Operating Expenses (OpEx)]
```dax
Monthly OpEx = 
SUM('Fact_Finance'[opex])
```
* **Format:** `₹#,##0`

### [Monthly Salaries]
```dax
Monthly Salaries = 
SUM('Fact_Finance'[salaries])
```
* **Format:** `₹#,##0`

### [Monthly Net Profit / (Loss)]
```dax
Monthly Net Profit = 
SUM('Fact_Finance'[net_profit])
```
* **Format:** `₹#,##0`

### [Trailing 3M Average Net Burn]
```dax
Trailing 3M Net Burn = 
VAR MaxMonth = MAX('Dim_Date'[month])
VAR Last3Months = 
    TOPN(
        3,
        FILTER(ALL('Fact_Finance'[month]), 'Fact_Finance'[month] <= MaxMonth),
        'Fact_Finance'[month],
        DESC
    )
RETURN
-CALCULATE(
    AVERAGE('Fact_Finance'[net_profit]),
    TREATAS(Last3Months, 'Fact_Finance'[month])
)
```
* **Format:** `₹#,##0`

### [Cash Runway (Months)]
```dax
Runway (Months) = 
DIVIDE(
    [Latest Cash Balance],
    [Trailing 3M Net Burn],
    99
)
```
* **Format:** `0.0 "Months"`

---

## 4. Operations, Fulfillment & Feedback Measures

### [Average Delivery Days]
```dax
Avg Delivery Days = 
CALCULATE(
    AVERAGE('Fact_Orders'[delivery_days]),
    'Fact_Orders'[status] = "Delivered"
)
```
* **Format:** `0.00 "days"`

### [Refund Rate %]
```dax
Refund Rate % = 
DIVIDE(
    [Refunded Orders],
    [Total Orders],
    0
)
```
* **Format:** `0.00%`

### [Customer Satisfaction Score (CSAT)]
```dax
CSAT Score = 
AVERAGE('Fact_Feedback'[csat_score])
```
* **Format:** `0.00 / 5.0`

### [NPS Promoters Count]
```dax
NPS Promoters = 
CALCULATE(
    COUNTROWS('Fact_Feedback'),
    'Fact_Feedback'[nps_score] >= 9
)
```

### [NPS Detractors Count]
```dax
NPS Detractors = 
CALCULATE(
    COUNTROWS('Fact_Feedback'),
    'Fact_Feedback'[nps_score] <= 6
)
```

### [Net Promoter Score (NPS)]
```dax
NPS Score = 
VAR TotalResponses = COUNTROWS('Fact_Feedback')
RETURN
IF(
    TotalResponses > 0,
    DIVIDE([NPS Promoters] - [NPS Detractors], TotalResponses, 0) * 100,
    BLANK()
)
```
* **Format:** `+0.0;-0.0;0.0`

---

## 5. Unit Economics & Strategic Growth Measures

### [Average Revenue Per User (ARPU)]
```dax
Monthly ARPU = 
DIVIDE(
    [MRR],
    [Active Customers],
    0
)
```
* **Format:** `₹#,##0`

### [Monthly Churn Rate %]
```dax
Monthly Churn % = 
VAR CurrentDate = MAX('Dim_Date'[date])
VAR StartDate = MIN('Dim_Date'[date])
VAR ActiveStart = 
    CALCULATE(
        DISTINCTCOUNT('Dim_Customer'[customer_id]),
        'Dim_Customer'[signup_date] < StartDate,
        ISBLANK('Dim_Customer'[churn_date]) || 'Dim_Customer'[churn_date] >= StartDate,
        ALL('Dim_Date')
    )
VAR ChurnCount = 
    CALCULATE(
        DISTINCTCOUNT('Dim_Customer'[customer_id]),
        'Dim_Customer'[churn_date] >= StartDate,
        'Dim_Customer'[churn_date] <= CurrentDate,
        ALL('Dim_Date')
    )
RETURN
DIVIDE(ChurnCount, ActiveStart, 0.05)
```
* **Format:** `0.00%`

### [Customer Lifetime Value (LTV)]
```dax
LTV = 
VAR ChurnClean = IF([Monthly Churn %] <= 0, 0.05, [Monthly Churn %])
RETURN
DIVIDE(
    [Monthly ARPU] * [Gross Margin %],
    ChurnClean,
    0
)
```
* **Format:** `₹#,##0`

### [LTV to CAC Ratio]
```dax
LTV:CAC Ratio = 
DIVIDE(
    [LTV],
    [CAC],
    BLANK()
)
```
* **Format:** `0.00x`

---

## 6. Time Intelligence & Week-over-Week (WoW) Measures

### [Delivered Revenue Prior Week]
```dax
Delivered Revenue PW = 
CALCULATE(
    [Delivered Revenue],
    DATEADD('Dim_Date'[date], -7, DAY)
)
```

### [Revenue WoW Change %]
```dax
Revenue WoW % = 
DIVIDE(
    [Delivered Revenue] - [Delivered Revenue PW],
    [Delivered Revenue PW],
    BLANK()
)
```
* **Format:** `+0.0%;-0.0%;0.0%`

### [Revenue WoW Indicator]
```dax
Revenue WoW KPI Icon = 
IF(
    [Revenue WoW %] >= 0,
    "▲ +" & FORMAT([Revenue WoW %], "0.0%"),
    "▼ " & FORMAT([Revenue WoW %], "0.0%")
)
```

### [MRR Prior Week]
```dax
MRR PW = 
CALCULATE(
    [MRR],
    DATEADD('Dim_Date'[date], -7, DAY)
)
```

### [MRR WoW Change %]
```dax
MRR WoW % = 
DIVIDE(
    [MRR] - [MRR PW],
    [MRR PW],
    BLANK()
)
```
* **Format:** `+0.0%;-0.0%;0.0%`

### [CAC Prior Week]
```dax
CAC PW = 
CALCULATE(
    [CAC],
    DATEADD('Dim_Date'[date], -7, DAY)
)
```

### [CAC WoW Change %]
```dax
CAC WoW % = 
DIVIDE(
    [CAC] - [CAC PW],
    [CAC PW],
    BLANK()
)
```
* **Format:** `+0.0%;-0.0%;0.0%`

### [Orders WoW Change %]
```dax
Orders WoW % = 
VAR OrdersPW = CALCULATE([Total Orders], DATEADD('Dim_Date'[date], -7, DAY))
RETURN
DIVIDE(
    [Total Orders] - OrdersPW,
    OrdersPW,
    BLANK()
)
```
* **Format:** `+0.0%;-0.0%;0.0%`

### [Refund Rate WoW Delta]
```dax
Refund Rate WoW Delta = 
VAR RefundPW = CALCULATE([Refund Rate %], DATEADD('Dim_Date'[date], -7, DAY))
RETURN
[Refund Rate %] - RefundPW
```
* **Format:** `+0.00%;-0.00%;0.00%`
