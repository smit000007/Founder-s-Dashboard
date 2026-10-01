"""
NutriBox KPI Calculation Engine
Computes weekly KPI values, week-over-week (WoW) changes, and channel-level unit economics.
"""

import os
import pandas as pd
import numpy as np

def compute_kpis(data_dir="data"):
    # Load all tables
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    subscriptions = pd.read_csv(os.path.join(data_dir, "subscriptions.csv"))
    marketing = pd.read_csv(os.path.join(data_dir, "marketing.csv"))
    finance = pd.read_csv(os.path.join(data_dir, "finance.csv"))
    feedback = pd.read_csv(os.path.join(data_dir, "feedback.csv"))
    date_table = pd.read_csv(os.path.join(data_dir, "date_table.csv"))

    # Merge dates with orders, marketing, feedback
    orders = orders.merge(date_table[["date", "week", "month", "quarter", "year"]], on="date", how="left")
    marketing = marketing.merge(date_table[["date", "week", "month"]], on="date", how="left")
    feedback = feedback.merge(date_table[["date", "week", "month"]], on="date", how="left")

    weeks = sorted(date_table["week"].unique())

    # Pre-parse customer dates
    customers["signup_date_dt"] = pd.to_datetime(customers["signup_date"])
    customers["churn_date_dt"] = pd.to_datetime(customers["churn_date"])

    # Prepare weekly finance lookup
    # Finance is monthly; allocate weekly share (~month / 4.333) or match cash balance
    finance_dict = finance.set_index("month").to_dict(orient="index")

    weekly_records = []

    for w in weeks:
        w_dates = date_table[date_table["week"] == w]
        w_start = pd.to_datetime(w_dates["date"].min())
        w_end = pd.to_datetime(w_dates["date"].max())
        m_str = w_dates["month"].iloc[0]

        # 1. Orders / Sales Metrics
        w_orders = orders[orders["week"] == w]
        w_delivered = w_orders[w_orders["status"] == "Delivered"]
        w_refunded = w_orders[w_orders["status"] == "Refunded"]
        w_pending = w_orders[w_orders["status"] == "Pending"]

        order_count = len(w_orders)
        delivered_rev = float(w_delivered["revenue"].sum())
        delivered_cogs = float(w_delivered["cogs"].sum())
        gross_profit = delivered_rev - delivered_cogs
        gross_margin_pct = (gross_profit / delivered_rev * 100) if delivered_rev > 0 else 0.0

        # Active customers at week end
        active_mask = (customers["signup_date_dt"] <= w_end) & (
            customers["churn_date_dt"].isna() | (customers["churn_date_dt"] > w_end)
        )
        active_customers = int(active_mask.sum())

        # Active customers at week start
        active_start_mask = (customers["signup_date_dt"] < w_start) & (
            customers["churn_date_dt"].isna() | (customers["churn_date_dt"] >= w_start)
        )
        active_start_count = int(active_start_mask.sum())

        # New signups this week
        new_signups = int(((customers["signup_date_dt"] >= w_start) & (customers["signup_date_dt"] <= w_end)).sum())

        # Churned customers this week
        churns = int(((customers["churn_date_dt"] >= w_start) & (customers["churn_date_dt"] <= w_end)).sum())
        weekly_churn_pct = (churns / active_start_count * 100) if active_start_count > 0 else 0.0
        monthly_churn_pct = weekly_churn_pct * 4.333

        # MRR: active subscriptions * price
        active_cust_ids = set(customers[active_mask]["customer_id"])
        w_active_subs = subscriptions[subscriptions["customer_id"].isin(active_cust_ids)]
        mrr = float(w_active_subs["monthly_price"].sum())
        arr = mrr * 12.0

        # 2. Marketing Metrics
        w_mktg = marketing[marketing["week"] == w]
        spend = float(w_mktg["spend"].sum())
        impressions = int(w_mktg["impressions"].sum())
        clicks = int(w_mktg["clicks"].sum())
        conversions = int(w_mktg["conversions"].sum())
        ad_rev = float(w_mktg["ad_revenue"].sum())

        cac = (spend / new_signups) if new_signups > 0 else 0.0
        roas = (ad_rev / spend) if spend > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        cvr = (conversions / clicks * 100) if clicks > 0 else 0.0

        # 3. Operations Metrics
        pending_count = len(w_pending)
        refund_count = len(w_refunded)
        refund_pct = (refund_count / order_count * 100) if order_count > 0 else 0.0
        avg_deliv_days = float(w_delivered["delivery_days"].mean()) if len(w_delivered) > 0 else 0.0

        w_feedback = feedback[feedback["week"] == w]
        csat = float(w_feedback["csat_score"].mean()) if len(w_feedback) > 0 else 0.0

        # NPS Calculation: % Promoters (9-10) - % Detractors (0-6)
        if len(w_feedback) > 0:
            promoters = (w_feedback["nps_score"] >= 9).sum()
            detractors = (w_feedback["nps_score"] <= 6).sum()
            total_nps_resp = len(w_feedback)
            nps = float((promoters - detractors) / total_nps_resp * 100)
        else:
            nps = 0.0

        # 4. Finance & Unit Economics
        # Monthly finance values mapped
        fin_row = finance_dict.get(m_str, list(finance_dict.values())[-1])
        monthly_opex = fin_row["opex"]
        monthly_salaries = fin_row["salaries"]
        latest_cash = fin_row["cash_balance"]

        # Weekly allocated opex & salaries
        weekly_opex = monthly_opex / 4.333
        weekly_salaries = monthly_salaries / 4.333
        weekly_net_profit = delivered_rev - delivered_cogs - spend - weekly_opex - weekly_salaries
        weekly_burn_rate = -weekly_net_profit if weekly_net_profit < 0 else 0.0
        monthly_net_burn = weekly_burn_rate * 4.333
        runway_months = (latest_cash / monthly_net_burn) if monthly_net_burn > 0 else 99.0

        # LTV: ARPU * GM% / Monthly Churn %
        # ARPU (Monthly) = MRR / Active Customers
        arpu = (mrr / active_customers) if active_customers > 0 else 0.0
        effective_churn = max(0.02, monthly_churn_pct / 100.0)
        ltv = (arpu * (gross_margin_pct / 100.0)) / effective_churn if effective_churn > 0 else 0.0
        ltv_cac_ratio = (ltv / cac) if cac > 0 else 0.0

        weekly_records.append({
            "week": w,
            "month": m_str,
            "revenue": delivered_rev,
            "mrr": mrr,
            "arr": arr,
            "orders": order_count,
            "customers": active_customers,
            "new_signups": new_signups,
            "churns": churns,
            "churn_pct": monthly_churn_pct,
            "gross_profit": gross_profit,
            "gross_margin_pct": gross_margin_pct,
            "marketing_spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "ad_revenue": ad_rev,
            "cac": cac,
            "roas": roas,
            "ctr": ctr,
            "cpc": cpc,
            "conversion_pct": cvr,
            "pending_orders": pending_count,
            "refund_pct": refund_pct,
            "avg_delivery_time": avg_deliv_days,
            "csat": csat,
            "nps": nps,
            "weekly_net_profit": weekly_net_profit,
            "burn_rate": monthly_net_burn,
            "cash_balance": latest_cash,
            "runway_months": runway_months,
            "arpu": arpu,
            "ltv": ltv,
            "ltv_cac": ltv_cac_ratio
        })

    df_weekly = pd.DataFrame(weekly_records)

    # Compute WoW Changes
    metrics_to_diff = [
        "revenue", "mrr", "arr", "orders", "customers", "new_signups", "marketing_spend",
        "cac", "roas", "ctr", "cpc", "conversion_pct", "gross_margin_pct", "refund_pct",
        "avg_delivery_time", "csat", "nps", "weekly_net_profit", "burn_rate", "runway_months", "ltv_cac"
    ]
    for col in metrics_to_diff:
        df_weekly[f"{col}_wow_val"] = df_weekly[col].diff()
        df_weekly[f"{col}_wow_pct"] = df_weekly[col].pct_change() * 100

    # Save to CSV
    output_path = os.path.join(data_dir, "weekly_kpis.csv")
    df_weekly.to_csv(output_path, index=False)
    print(f"Weekly KPIs computed and saved to {output_path} ({len(df_weekly)} weeks)")

    # -----------------------------------------------------------------
    # Print Executive KPI Snapshot (Week 52 vs Week 51)
    # -----------------------------------------------------------------
    curr_wk = df_weekly.iloc[-1]
    prev_wk = df_weekly.iloc[-2]

    print("\n" + "="*80)
    print(f"FOUNDER'S OFFICE EXECUTIVE KPI REPORT: {curr_wk['week']} vs {prev_wk['week']}")
    print("="*80)

    def fmt_change(curr, prev, is_pct=False, is_inverted=False):
        chg = curr - prev
        pct = ((curr - prev) / prev * 100) if prev != 0 else 0
        sign = "+" if chg >= 0 else ""
        # Green / Red indicator check
        is_good = (chg <= 0) if is_inverted else (chg >= 0)
        indicator = "[UP]" if chg >= 0 else "[DN]"
        if is_pct:
            return f"{curr:.2f}% ({sign}{chg:.2f} pts WoW) {indicator}"
        else:
            return f"{curr:,.2f} ({sign}{pct:.1f}% WoW) {indicator}"

    print(f"{'CATEGORY':<14} | {'METRIC':<20} | {'PREV (W51)':<16} | {'CURR (W52)':<16} | {'WoW CHANGE':<18}")
    print("-" * 88)
    
    rows = [
        ("Sales", "Delivered Revenue", f"INR {prev_wk['revenue']:,.0f}", f"INR {curr_wk['revenue']:,.0f}", fmt_change(curr_wk['revenue'], prev_wk['revenue'])),
        ("Sales", "MRR", f"INR {prev_wk['mrr']:,.0f}", f"INR {curr_wk['mrr']:,.0f}", fmt_change(curr_wk['mrr'], prev_wk['mrr'])),
        ("Sales", "ARR", f"INR {prev_wk['arr']:,.0f}", f"INR {curr_wk['arr']:,.0f}", fmt_change(curr_wk['arr'], prev_wk['arr'])),
        ("Sales", "Orders Placed", f"{prev_wk['orders']:.0f}", f"{curr_wk['orders']:.0f}", fmt_change(curr_wk['orders'], prev_wk['orders'])),
        ("Marketing", "Marketing Spend", f"INR {prev_wk['marketing_spend']:,.0f}", f"INR {curr_wk['marketing_spend']:,.0f}", fmt_change(curr_wk['marketing_spend'], prev_wk['marketing_spend'], is_inverted=True)),
        ("Marketing", "CAC", f"INR {prev_wk['cac']:,.0f}", f"INR {curr_wk['cac']:,.0f}", fmt_change(curr_wk['cac'], prev_wk['cac'], is_inverted=True)),
        ("Marketing", "ROAS", f"{prev_wk['roas']:.2f}x", f"{curr_wk['roas']:.2f}x", fmt_change(curr_wk['roas'], prev_wk['roas'])),
        ("Marketing", "CTR", f"{prev_wk['ctr']:.2f}%", f"{curr_wk['ctr']:.2f}%", fmt_change(curr_wk['ctr'], prev_wk['ctr'], is_pct=True)),
        ("Marketing", "Conversion %", f"{prev_wk['conversion_pct']:.2f}%", f"{curr_wk['conversion_pct']:.2f}%", fmt_change(curr_wk['conversion_pct'], prev_wk['conversion_pct'], is_pct=True)),
        ("Finance", "Gross Margin %", f"{prev_wk['gross_margin_pct']:.2f}%", f"{curr_wk['gross_margin_pct']:.2f}%", fmt_change(curr_wk['gross_margin_pct'], prev_wk['gross_margin_pct'], is_pct=True)),
        ("Finance", "Net Burn (Mo)", f"INR {prev_wk['burn_rate']:,.0f}", f"INR {curr_wk['burn_rate']:,.0f}", fmt_change(curr_wk['burn_rate'], prev_wk['burn_rate'], is_inverted=True)),
        ("Finance", "Runway (Months)", f"{prev_wk['runway_months']:.1f} mos", f"{curr_wk['runway_months']:.1f} mos", fmt_change(curr_wk['runway_months'], prev_wk['runway_months'])),
        ("Operations", "Pending Orders", f"{prev_wk['pending_orders']:.0f}", f"{curr_wk['pending_orders']:.0f}", fmt_change(curr_wk['pending_orders'], prev_wk['pending_orders'], is_inverted=True)),
        ("Operations", "Refund Rate %", f"{prev_wk['refund_pct']:.2f}%", f"{curr_wk['refund_pct']:.2f}%", fmt_change(curr_wk['refund_pct'], prev_wk['refund_pct'], is_pct=True, is_inverted=True)),
        ("Operations", "Avg Delivery Days", f"{prev_wk['avg_delivery_time']:.2f} days", f"{curr_wk['avg_delivery_time']:.2f} days", fmt_change(curr_wk['avg_delivery_time'], prev_wk['avg_delivery_time'], is_inverted=True)),
        ("Operations", "CSAT (1-5)", f"{prev_wk['csat']:.2f}", f"{curr_wk['csat']:.2f}", fmt_change(curr_wk['csat'], prev_wk['csat'])),
        ("Operations", "NPS (-100 to +100)", f"{prev_wk['nps']:.1f}", f"{curr_wk['nps']:.1f}", fmt_change(curr_wk['nps'], prev_wk['nps'])),
        ("Business", "Active Customers", f"{prev_wk['customers']:.0f}", f"{curr_wk['customers']:.0f}", fmt_change(curr_wk['customers'], prev_wk['customers'])),
        ("Business", "Monthly Churn %", f"{prev_wk['churn_pct']:.2f}%", f"{curr_wk['churn_pct']:.2f}%", fmt_change(curr_wk['churn_pct'], prev_wk['churn_pct'], is_pct=True, is_inverted=True)),
        ("Business", "LTV:CAC Ratio", f"{prev_wk['ltv_cac']:.2f}x", f"{curr_wk['ltv_cac']:.2f}x", fmt_change(curr_wk['ltv_cac'], prev_wk['ltv_cac']))
    ]

    for cat, metric, p_val, c_val, change in rows:
        print(f"{cat:<14} | {metric:<20} | {p_val:<16} | {c_val:<16} | {change:<18}")

    print("="*80 + "\n")

    # -----------------------------------------------------------------
    # Channel Level Summary (Lifetime & Week 52)
    # -----------------------------------------------------------------
    print("CHANNEL PERFORMANCE SUMMARY (LIFETIME 52 WEEKS):")
    chan_summary = marketing.groupby("channel").agg(
        total_spend=("spend", "sum"),
        total_impr=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_conv=("conversions", "sum"),
        total_ad_rev=("ad_revenue", "sum")
    ).reset_index()

    chan_summary["ROAS"] = chan_summary["total_ad_rev"] / chan_summary["total_spend"]
    chan_summary["CTR%"] = chan_summary["total_clicks"] / chan_summary["total_impr"] * 100
    chan_summary["CPC"] = chan_summary["total_spend"] / chan_summary["total_clicks"]
    chan_summary["CVR%"] = chan_summary["total_conv"] / chan_summary["total_clicks"] * 100

    # Add acquired customer count and CAC
    cust_by_chan = customers.groupby("acquisition_channel")["customer_id"].count().to_dict()
    chan_summary["new_customers"] = chan_summary["channel"].map(cust_by_chan)
    chan_summary["CAC"] = chan_summary["total_spend"] / chan_summary["new_customers"]

    for _, r in chan_summary.sort_values("ROAS", ascending=False).iterrows():
        print(f" - {r['channel']:<10}: Spend=INR {r['total_spend']:>10,.0f} | Cust={r['new_customers']:>4} | CAC=INR {r['CAC']:>6,.0f} | ROAS={r['ROAS']:>5.2f}x | CVR={r['CVR%']:>5.2f}%")

    print("\n" + "="*80)
    return df_weekly

if __name__ == "__main__":
    compute_kpis(data_dir="data")
