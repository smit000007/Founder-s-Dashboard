"""
NutriBox Synthetic Data Generator
Generates realistic D2C healthy snack subscription data for 12 months (52 weeks).
Currency: INR (₹)
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

def generate_all_data(output_dir="data", seed=42):
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker('en_IN')
    Faker.seed(seed)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating synthetic dataset for NutriBox in '{output_dir}'...")

    # -------------------------------------------------------------
    # 1. Date Range Setup (52 full weeks: 2023-10-02 to 2024-09-29)
    # -------------------------------------------------------------
    start_date = datetime(2023, 10, 2)  # Monday
    end_date = datetime(2024, 9, 29)    # Sunday
    date_list = [start_date + timedelta(days=d) for d in range((end_date - start_date).days + 1)]

    # Build date_table
    date_records = []
    for d in date_list:
        # ISO calendar week
        iso_year, iso_week, iso_weekday = d.isocalendar()
        # Calculate standard project week index from 1 to 52
        week_idx = ((d - start_date).days // 7) + 1
        date_records.append({
            "date": d.strftime("%Y-%m-%d"),
            "week": f"W{week_idx:02d}",
            "week_start": (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d"),
            "month": d.strftime("%Y-%m"),
            "month_name": d.strftime("%B %Y"),
            "quarter": f"{d.year}-Q{(d.month - 1) // 3 + 1}",
            "year": d.year,
            "day_of_week": d.strftime("%A"),
            "is_weekend": 1 if d.weekday() >= 5 else 0
        })
    df_date = pd.DataFrame(date_records)
    df_date.to_csv(os.path.join(output_dir, "date_table.csv"), index=False)
    print(f"-> Saved date_table.csv ({len(df_date)} rows)")

    # -------------------------------------------------------------
    # 2. Customers & Subscriptions Setup (~1,280 customers)
    # -------------------------------------------------------------
    num_customers = 1280
    channels = ["Instagram", "Google", "Facebook", "Email", "Referral"]
    channel_weights = [0.38, 0.26, 0.18, 0.08, 0.10]
    cities = ["Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai"]
    city_weights = [0.32, 0.24, 0.20, 0.10, 0.08, 0.06]

    plans = {
        "Weekly Snack Box": {"monthly_price": 1899, "weight": 0.28, "boxes_per_month": 4},
        "Bi-Weekly Munch": {"monthly_price": 1199, "weight": 0.38, "boxes_per_month": 2},
        "Monthly Fitness Box": {"monthly_price": 1499, "weight": 0.24, "boxes_per_month": 1},
        "Family Mega Box": {"monthly_price": 2499, "weight": 0.10, "boxes_per_month": 2}
    }
    plan_names = list(plans.keys())
    plan_weights = [plans[p]["weight"] for p in plan_names]

    customers = []
    subscriptions = []

    # Distribution of customer signups across the 364 days with steady growth & holiday bumps
    # Baseline growth: more signups as the business matures
    signup_weights = []
    for d in date_list:
        day_idx = (d - start_date).days
        # Base upward trend
        trend = 1.0 + 1.6 * (day_idx / 364.0)
        # Seasonal bump: Diwali (Nov 2023 - days 30-50), New Year Fitness (Jan 2024 - days 90-120)
        seasonal = 1.0
        if 35 <= day_idx <= 55:  # Festive season
            seasonal = 1.35
        elif 90 <= day_idx <= 125: # Jan fitness resolutions
            seasonal = 1.45
        elif 240 <= day_idx <= 260: # Summer wellness sale
            seasonal = 1.20
        signup_weights.append(trend * seasonal)
    signup_weights = np.array(signup_weights) / sum(signup_weights)

    # Assign signup dates
    signup_indices = np.random.choice(len(date_list), size=num_customers, p=signup_weights)
    signup_indices.sort()

    for i in range(num_customers):
        c_id = f"CUST-{1001 + i}"
        s_date = date_list[signup_indices[i]]
        channel = random.choices(channels, weights=channel_weights)[0]
        city = random.choices(cities, weights=city_weights)[0]
        plan = random.choices(plan_names, weights=plan_weights)[0]
        monthly_price = plans[plan]["monthly_price"]

        # Realistic churn logic: 4-6% monthly churn rate
        # Lifespan modeled using exponential / geometric distribution
        # Tenure average ~ 6-8 months
        days_since_signup = (end_date - s_date).days
        # Monthly churn probability ~ 5%
        # Survival prob after m months = (1 - 0.05)^m
        months_possible = max(1, days_since_signup / 30.4)
        has_churned = False
        churn_date = None

        if days_since_signup > 20: # Needs some time to churn
            churn_risk = 1.0 - ((1.0 - 0.048) ** months_possible)
            # Instagram leads have slightly higher churn
            if channel == "Instagram":
                churn_risk = min(0.85, churn_risk * 1.15)
            elif channel == "Referral":
                churn_risk = churn_risk * 0.75

            if random.random() < churn_risk:
                has_churned = True
                # Pick churn day between 20 days after signup and end_date
                churn_day_offset = random.randint(20, max(21, days_since_signup))
                c_date = s_date + timedelta(days=churn_day_offset)
                if c_date <= end_date:
                    churn_date = c_date.strftime("%Y-%m-%d")
                else:
                    has_churned = False

        is_active = 0 if has_churned else 1

        customers.append({
            "customer_id": c_id,
            "signup_date": s_date.strftime("%Y-%m-%d"),
            "plan": plan,
            "acquisition_channel": channel,
            "city": city,
            "is_active": is_active,
            "churn_date": churn_date if has_churned else ""
        })

        subscriptions.append({
            "subscription_id": f"SUB-{2001 + i}",
            "customer_id": c_id,
            "plan": plan,
            "monthly_price": monthly_price,
            "start_date": s_date.strftime("%Y-%m-%d"),
            "end_date": churn_date if has_churned else ""
        })

    df_customers = pd.DataFrame(customers)
    df_subscriptions = pd.DataFrame(subscriptions)

    df_customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
    df_subscriptions.to_csv(os.path.join(output_dir, "subscriptions.csv"), index=False)
    print(f"-> Saved customers.csv ({len(df_customers)} rows)")
    print(f"-> Saved subscriptions.csv ({len(df_subscriptions)} rows)")

    # -------------------------------------------------------------
    # 3. Products Definition
    # -------------------------------------------------------------
    products = {
        "NutriMix Berries & Nuts": {"price": 549, "cogs_pct": 0.48, "weight": 0.28},
        "Protein Trail Crunch": {"price": 649, "cogs_pct": 0.50, "weight": 0.25},
        "Keto Seeds Delight": {"price": 599, "cogs_pct": 0.49, "weight": 0.20},  # Quality defect in W46!
        "Millet Energy Crisp": {"price": 449, "cogs_pct": 0.46, "weight": 0.15},
        "Dark Cocoa Roasted Almonds": {"price": 699, "cogs_pct": 0.52, "weight": 0.12}
    }
    prod_names = list(products.keys())
    prod_weights = [products[p]["weight"] for p in prod_names]

    # -------------------------------------------------------------
    # 4. Orders Setup (~15,000 rows)
    # -------------------------------------------------------------
    # Active subscriptions generate recurring box shipments + add-on repeat orders
    cust_dict = {c["customer_id"]: c for c in customers}
    orders = []
    order_counter = 10001

    # To guarantee ~15,000 orders across 364 days, we generate recurring box deliveries
    # plus occasional extra snack add-ons for active customers
    for c in customers:
        c_id = c["customer_id"]
        s_date = datetime.strptime(c["signup_date"], "%Y-%m-%d")
        c_date = datetime.strptime(c["churn_date"], "%Y-%m-%d") if c["churn_date"] else end_date
        plan = c["plan"]
        channel = c["acquisition_channel"]
        boxes_per_month = plans[plan]["boxes_per_month"]
        interval_days = 28 // boxes_per_month

        curr = s_date
        while curr <= c_date and curr <= end_date:
            # Order date: allow small jitter around delivery schedule
            jitter = random.randint(0, 2)
            ord_date = curr + timedelta(days=jitter)
            if ord_date > end_date:
                break

            # Product selection
            prod = random.choices(prod_names, weights=prod_weights)[0]
            unit_price = products[prod]["price"]
            quantity = random.choices([1, 2, 3], weights=[0.82, 0.14, 0.04])[0]
            rev = unit_price * quantity
            cogs = round(rev * products[prod]["cogs_pct"], 2)

            # Check week index for the specific scenario:
            # Week 46 (around mid-August 2024, days ~ 315-321) has a refund spike tied to "Keto Seeds Delight"
            week_idx = ((ord_date - start_date).days // 7) + 1

            # Realistic delivery days: 2 to 7 days
            deliv_days = random.choices([2, 3, 4, 5, 6, 7], weights=[0.15, 0.35, 0.28, 0.14, 0.05, 0.03])[0]

            # Status determination
            # Recent orders in last 4 days may be Pending
            days_from_end = (end_date - ord_date).days
            if days_from_end <= 3 and random.random() < 0.40:
                status = "Pending"
                refund_flag = 0
            else:
                # Default refund rate is ~1.8% to 2.2%
                refund_prob = 0.018
                if week_idx == 46 and prod == "Keto Seeds Delight":
                    refund_prob = 0.28  # Dramatic spike! Packaging seal defect leading to rancidity
                elif week_idx == 47 and prod == "Keto Seeds Delight":
                    refund_prob = 0.12  # Lingering tail of returns

                if random.random() < refund_prob:
                    status = "Refunded"
                    refund_flag = 1
                else:
                    status = "Delivered"
                    refund_flag = 0

            orders.append({
                "order_id": f"ORD-{order_counter}",
                "date": ord_date.strftime("%Y-%m-%d"),
                "customer_id": c_id,
                "product": prod,
                "quantity": quantity,
                "revenue": rev,
                "cogs": cogs,
                "status": status,
                "channel": channel,
                "delivery_days": deliv_days,
                "refund_flag": refund_flag
            })
            order_counter += 1
            curr += timedelta(days=interval_days)

    df_orders = pd.DataFrame(orders)
    # Sort orders by date
    df_orders = df_orders.sort_values("date").reset_index(drop=True)
    df_orders.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    print(f"-> Saved orders.csv ({len(df_orders)} rows)")

    # -------------------------------------------------------------
    # 5. Marketing Setup (Daily spend & funnel for 5 channels)
    # -------------------------------------------------------------
    # Channels: Instagram, Google, Facebook, Email, Referral
    # Nuance:
    # - Instagram: High spend, tons of impressions/clicks, but low conversion & poor ROAS (< 1.0)
    # - Google: Strong intent, high conversion, solid ROAS (2.5 - 3.2x)
    # - Facebook: Moderate performance, ROAS ~ 1.7 - 2.0x
    # - Email: Very low cost, high conversion, ROAS 6.0 - 9.0x
    # - Referral: Reward payout cost, organic viral loop, ROAS 4.0 - 5.5x
    marketing_rows = []
    
    # Pre-calculate actual order conversions by date and channel to make it cohesive
    orders_by_date_channel = df_orders.groupby(["date", "channel"]).agg(
        order_count=("order_id", "count"),
        order_rev=("revenue", lambda x: sum(x[df_orders.loc[x.index, "status"] == "Delivered"]))
    ).reset_index()
    orders_dict = {(r["date"], r["channel"]): (r["order_count"], r["order_rev"]) for _, r in orders_by_date_channel.iterrows()}

    for d in date_list:
        d_str = d.strftime("%Y-%m-%d")
        day_idx = (d - start_date).days
        trend = 1.0 + 0.8 * (day_idx / 364.0)
        
        # Instagram: Budget-heavy influencer & story ads
        # Spend ~ ₹7,000 - ₹12,000/day. High CPM/CPC, low CVR (~1.2%)
        ig_spend = round(random.uniform(7500, 11500) * trend, 2)
        ig_cpm = random.uniform(140, 180)
        ig_impr = int((ig_spend / ig_cpm) * 1000)
        ig_ctr = random.uniform(0.016, 0.024)
        ig_clicks = int(ig_impr * ig_ctr)
        ig_cvr = random.uniform(0.011, 0.016)
        ig_conv = max(1, int(ig_clicks * ig_cvr))
        # Poor ROAS: revenue barely covers or fails to cover spend (ROAS 0.70 - 0.88x)
        ig_ad_rev = round(ig_spend * random.uniform(0.72, 0.86), 2)
        marketing_rows.append({
            "date": d_str, "channel": "Instagram", "spend": ig_spend,
            "impressions": ig_impr, "clicks": ig_clicks, "conversions": ig_conv, "ad_revenue": ig_ad_rev
        })

        # Google Search & Performance Max:
        # High intent, spend ₹5,500 - ₹9,000/day, high CVR (~3.8%), ROAS 2.6 - 3.2x
        goog_spend = round(random.uniform(5500, 9000) * trend, 2)
        goog_cpm = random.uniform(220, 290)
        goog_impr = int((goog_spend / goog_cpm) * 1000)
        goog_ctr = random.uniform(0.035, 0.048)
        goog_clicks = int(goog_impr * goog_ctr)
        goog_cvr = random.uniform(0.034, 0.045)
        goog_conv = max(1, int(goog_clicks * goog_cvr))
        goog_ad_rev = round(goog_spend * random.uniform(2.65, 3.15), 2)
        marketing_rows.append({
            "date": d_str, "channel": "Google", "spend": goog_spend,
            "impressions": goog_impr, "clicks": goog_clicks, "conversions": goog_conv, "ad_revenue": goog_ad_rev
        })

        # Facebook / Meta Lookalike:
        # Spend ₹3,500 - ₹6,000/day, ROAS ~ 1.7 - 2.1x
        fb_spend = round(random.uniform(3500, 6000) * trend, 2)
        fb_cpm = random.uniform(120, 160)
        fb_impr = int((fb_spend / fb_cpm) * 1000)
        fb_ctr = random.uniform(0.022, 0.030)
        fb_clicks = int(fb_impr * fb_ctr)
        fb_cvr = random.uniform(0.024, 0.032)
        fb_conv = max(1, int(fb_clicks * fb_cvr))
        fb_ad_rev = round(fb_spend * random.uniform(1.75, 2.10), 2)
        marketing_rows.append({
            "date": d_str, "channel": "Facebook", "spend": fb_spend,
            "impressions": fb_impr, "clicks": fb_clicks, "conversions": fb_conv, "ad_revenue": fb_ad_rev
        })

        # Email Marketing (Klaviyo / automation):
        # Low tooling/list maintenance spend ~ ₹800 - ₹1,400/day, high engagement & ROAS ~ 6-8x
        em_spend = round(random.uniform(800, 1400) * trend, 2)
        em_impr = random.randint(12000, 22000) # Emails sent / delivered
        em_ctr = random.uniform(0.055, 0.085)  # Click-to-open
        em_clicks = int(em_impr * em_ctr)
        em_cvr = random.uniform(0.040, 0.060)
        em_conv = max(1, int(em_clicks * em_cvr))
        em_ad_rev = round(em_spend * random.uniform(6.5, 8.8), 2)
        marketing_rows.append({
            "date": d_str, "channel": "Email", "spend": em_spend,
            "impressions": em_impr, "clicks": em_clicks, "conversions": em_conv, "ad_revenue": em_ad_rev
        })

        # Referral Program:
        # Modest referral credits/payouts spend ~ ₹1,200 - ₹2,200/day, high conversion, ROAS ~ 4.2 - 5.5x
        ref_spend = round(random.uniform(1200, 2200) * trend, 2)
        ref_impr = random.randint(4000, 8000)
        ref_ctr = random.uniform(0.070, 0.110)
        ref_clicks = int(ref_impr * ref_ctr)
        ref_cvr = random.uniform(0.065, 0.095)
        ref_conv = max(1, int(ref_clicks * ref_cvr))
        ref_ad_rev = round(ref_spend * random.uniform(4.2, 5.4), 2)
        marketing_rows.append({
            "date": d_str, "channel": "Referral", "spend": ref_spend,
            "impressions": ref_impr, "clicks": ref_clicks, "conversions": ref_conv, "ad_revenue": ref_ad_rev
        })

    df_marketing = pd.DataFrame(marketing_rows)
    df_marketing.to_csv(os.path.join(output_dir, "marketing.csv"), index=False)
    print(f"-> Saved marketing.csv ({len(df_marketing)} rows)")

    # -------------------------------------------------------------
    # 6. Customer Feedback (CSAT & NPS)
    # -------------------------------------------------------------
    # Tied to delivery experience.
    # Reflects the Week 46 Keto Seeds Delight packaging crisis!
    feedbacks = []
    # Sample about 65% of delivered orders to leave a CSAT rating, and periodic NPS
    delivered_orders = df_orders[df_orders["status"] == "Delivered"].copy()
    refunded_orders = df_orders[df_orders["status"] == "Refunded"].copy()

    for _, row in delivered_orders.sample(frac=0.55, random_state=seed).iterrows():
        c_id = row["customer_id"]
        ord_date = datetime.strptime(row["date"], "%Y-%m-%d")
        f_date = ord_date + timedelta(days=row["delivery_days"] + random.randint(0, 2))
        if f_date > end_date:
            continue
        
        # High baseline satisfaction
        csat = random.choices([5, 4, 3, 2, 1], weights=[0.60, 0.28, 0.08, 0.03, 0.01])[0]
        nps = random.choices([10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 
                             weights=[0.42, 0.28, 0.14, 0.06, 0.03, 0.02, 0.02, 0.01, 0.01, 0.005, 0.005])[0]

        feedbacks.append({
            "feedback_id": f"FB-{len(feedbacks)+1001}",
            "customer_id": c_id,
            "date": f_date.strftime("%Y-%m-%d"),
            "csat_score": csat,
            "nps_score": nps
        })

    # Refunded orders get very poor ratings!
    for _, row in refunded_orders.iterrows():
        c_id = row["customer_id"]
        ord_date = datetime.strptime(row["date"], "%Y-%m-%d")
        f_date = ord_date + timedelta(days=random.randint(2, 6))
        if f_date > end_date:
            continue

        csat = random.choices([1, 2, 3], weights=[0.80, 0.16, 0.04])[0]
        nps = random.choices([0, 1, 2, 3, 4], weights=[0.60, 0.25, 0.10, 0.03, 0.02])[0]
        feedbacks.append({
            "feedback_id": f"FB-{len(feedbacks)+1001}",
            "customer_id": c_id,
            "date": f_date.strftime("%Y-%m-%d"),
            "csat_score": csat,
            "nps_score": nps
        })

    df_feedback = pd.DataFrame(feedbacks)
    df_feedback = df_feedback.sort_values("date").reset_index(drop=True)
    df_feedback.to_csv(os.path.join(output_dir, "feedback.csv"), index=False)
    print(f"-> Saved feedback.csv ({len(df_feedback)} rows)")

    # -------------------------------------------------------------
    # 7. Finance Setup & Reconciliation
    # -------------------------------------------------------------
    # Must reconcile with:
    # 1. Monthly revenue from delivered orders (or net revenue after refunds)
    # 2. Monthly COGS from orders
    # 3. Monthly marketing spend from marketing.csv
    # 4. Realistic salaries, OPEX (logistics/cloud/packaging)
    # 5. Starting cash balance ~ ₹2.2 Crores (₹22,000,000), burning down to ~ ₹1.6 - ₹1.8 Crores
    #    with ~8-10 months runway left at net burn!
    
    # Calculate monthly delivered revenue and cogs
    df_orders["month"] = df_orders["date"].apply(lambda x: x[:7])
    df_marketing["month"] = df_marketing["date"].apply(lambda x: x[:7])

    # Reconcile revenue with delivered orders (standard accounting recognition)
    delivered_monthly = df_orders[df_orders["status"] == "Delivered"].groupby("month").agg(
        revenue=("revenue", "sum"),
        cogs=("cogs", "sum")
    ).reset_index()

    mktg_monthly = df_marketing.groupby("month")["spend"].sum().reset_index()
    mktg_monthly.rename(columns={"spend": "marketing_spend"}, inplace=True)

    finance_merged = pd.merge(delivered_monthly, mktg_monthly, on="month").sort_values("month").reset_index(drop=True)

    # Realistic OpEx and Salaries scaling as business grows
    # Base salaries: tech, ops, marketing
    # OpEx: Warehousing, cold-chain, AWS, office rent, packaging overheads
    temp_burns = []
    for idx, row in finance_merged.iterrows():
        rev = row["revenue"]
        cogs = row["cogs"]
        mktg = row["marketing_spend"]
        scale_factor = 1.0 + (idx / 12.0) * 0.45
        salaries = round(680000 * scale_factor, 2)
        opex = round(420000 * scale_factor + (rev * 0.04), 2)
        net_profit = rev - cogs - opex - salaries - mktg
        temp_burns.append(net_profit)

    # We want final cash balance / recent_3m_avg_net_burn to be ~8.8 - 9.2 months
    recent_3m_burn = -np.mean(temp_burns[-3:])
    target_end_cash = round(recent_3m_burn * 9.0, 2)
    total_cumulative_burn = -sum(temp_burns)
    starting_cash = round(target_end_cash + total_cumulative_burn, 2)

    current_cash = starting_cash
    finance_rows = []

    for idx, row in finance_merged.iterrows():
        m = row["month"]
        rev = round(row["revenue"], 2)
        cogs = round(row["cogs"], 2)
        mktg = round(row["marketing_spend"], 2)

        scale_factor = 1.0 + (idx / 12.0) * 0.45
        salaries = round(680000 * scale_factor, 2)
        opex = round(420000 * scale_factor + (rev * 0.04), 2)

        net_profit = round(rev - cogs - opex - salaries - mktg, 2)
        current_cash = round(current_cash + net_profit, 2)

        finance_rows.append({
            "month": m,
            "revenue": rev,
            "cogs": cogs,
            "opex": opex,
            "salaries": salaries,
            "marketing_spend": mktg,
            "cash_balance": current_cash,
            "net_profit": net_profit
        })

    df_finance = pd.DataFrame(finance_rows)
    df_finance.to_csv(os.path.join(output_dir, "finance.csv"), index=False)
    print(f"-> Saved finance.csv ({len(df_finance)} rows)")

    # -------------------------------------------------------------
    # 8. Validation & Integrity Check
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("DATA INTEGRITY & VALIDATION REPORT")
    print("="*60)
    
    # Check nulls
    null_counts = {
        "orders": df_orders.isnull().sum().to_dict(),
        "customers (ignoring churn_date)": df_customers[["customer_id", "signup_date", "plan", "acquisition_channel", "city", "is_active"]].isnull().sum().to_dict(),
        "subscriptions": df_subscriptions[["subscription_id", "customer_id", "plan", "monthly_price", "start_date"]].isnull().sum().to_dict(),
        "marketing": df_marketing.isnull().sum().to_dict(),
        "finance": df_finance.isnull().sum().to_dict(),
        "feedback": df_feedback.isnull().sum().to_dict(),
        "date_table": df_date.isnull().sum().to_dict()
    }
    has_nulls = False
    for t_name, n_dict in null_counts.items():
        bad = {k: v for k, v in n_dict.items() if v > 0}
        if bad:
            print(f"WARNING: Nulls detected in {t_name}: {bad}")
            has_nulls = True
    if not has_nulls:
        print("[PASS] All required primary and foreign keys have ZERO nulls.")

    # Reconcile Revenue
    orders_rev_total = df_orders[df_orders["status"] == "Delivered"]["revenue"].sum()
    finance_rev_total = df_finance["revenue"].sum()
    rev_diff = abs(orders_rev_total - finance_rev_total)
    print(f"Orders Delivered Revenue: INR {orders_rev_total:,.2f}")
    print(f"Finance Recognized Rev:   INR {finance_rev_total:,.2f}")
    print(f"Difference:                INR {rev_diff:.4f} -> {'[RECONCILED PASS]' if rev_diff < 0.01 else '[FAIL]'}")

    # Reconcile COGS
    orders_cogs_total = df_orders[df_orders["status"] == "Delivered"]["cogs"].sum()
    finance_cogs_total = df_finance["cogs"].sum()
    cogs_diff = abs(orders_cogs_total - finance_cogs_total)
    print(f"Orders COGS:              INR {orders_cogs_total:,.2f}")
    print(f"Finance COGS:             INR {finance_cogs_total:,.2f}")
    print(f"Difference:                INR {cogs_diff:.4f} -> {'[RECONCILED PASS]' if cogs_diff < 0.01 else '[FAIL]'}")

    # Reconcile Marketing Spend
    mktg_spend_total = df_marketing["spend"].sum()
    finance_mktg_total = df_finance["marketing_spend"].sum()
    mktg_diff = abs(mktg_spend_total - finance_mktg_total)
    print(f"Marketing CSV Spend:      INR {mktg_spend_total:,.2f}")
    print(f"Finance Marketing Spend:  INR {finance_mktg_total:,.2f}")
    print(f"Difference:                INR {mktg_diff:.4f} -> {'[RECONCILED PASS]' if mktg_diff < 0.01 else '[FAIL]'}")

    # Customer ID Integrity
    order_cust_unmatched = set(df_orders["customer_id"]) - set(df_customers["customer_id"])
    sub_cust_unmatched = set(df_subscriptions["customer_id"]) - set(df_customers["customer_id"])
    fb_cust_unmatched = set(df_feedback["customer_id"]) - set(df_customers["customer_id"])
    print(f"Unmatched Customer IDs in Orders:        {len(order_cust_unmatched)}")
    print(f"Unmatched Customer IDs in Subscriptions: {len(sub_cust_unmatched)}")
    print(f"Unmatched Customer IDs in Feedback:      {len(fb_cust_unmatched)}")
    if len(order_cust_unmatched) == 0 and len(sub_cust_unmatched) == 0 and len(fb_cust_unmatched) == 0:
        print("[PASS] Full Referential Integrity across all customer relations.")

    # Business Scenario Metrics check
    gross_margin_pct = (finance_rev_total - finance_cogs_total) / finance_rev_total * 100
    print(f"Average Gross Margin:     {gross_margin_pct:.2f}% (Target: 45-55%) -> {'[PASS]' if 45 <= gross_margin_pct <= 55 else '[CHECK]'}")

    # Runway calculation
    last_cash = df_finance.iloc[-1]["cash_balance"]
    last_net_burn = -df_finance.iloc[-1]["net_profit"] if df_finance.iloc[-1]["net_profit"] < 0 else 0
    avg_recent_burn = -df_finance.tail(3)["net_profit"].mean()
    runway_months = last_cash / avg_recent_burn if avg_recent_burn > 0 else 99
    print(f"Latest Cash Balance:      INR {last_cash:,.2f}")
    print(f"Average Recent Net Burn:  INR {avg_recent_burn:,.2f}/month")
    print(f"Estimated Runway:         {runway_months:.1f} months (Target: ~8-10 months) -> {'[PASS]' if 7.5 <= runway_months <= 11.0 else '[CHECK]'}")

    # Week 46 Refund Check
    df_orders_wk = pd.merge(df_orders, df_date[["date", "week"]], on="date")
    wk46_refunds = df_orders_wk[(df_orders_wk["week"] == "W46") & (df_orders_wk["product"] == "Keto Seeds Delight")]
    wk46_ref_rate = (wk46_refunds["status"] == "Refunded").mean() * 100
    baseline_ref_rate = (df_orders_wk[df_orders_wk["week"] != "W46"]["status"] == "Refunded").mean() * 100
    print(f"W46 'Keto Seeds Delight' Refund Rate: {wk46_ref_rate:.2f}% vs Baseline: {baseline_ref_rate:.2f}% -> {'[PASS]' if wk46_ref_rate > 15 else '[CHECK]'}")

    # Instagram ROAS Check
    ig_spend_sum = df_marketing[df_marketing["channel"] == "Instagram"]["spend"].sum()
    ig_rev_sum = df_marketing[df_marketing["channel"] == "Instagram"]["ad_revenue"].sum()
    ig_roas = ig_rev_sum / ig_spend_sum
    print(f"Instagram Overall ROAS:   {ig_roas:.2f}x (Target: Poor ROAS < 0.95x) -> {'[PASS]' if ig_roas < 0.95 else '[CHECK]'}")

    print("="*60 + "\n")

if __name__ == "__main__":
    generate_all_data(output_dir="data", seed=42)
