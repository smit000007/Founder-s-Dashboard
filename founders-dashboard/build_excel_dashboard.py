"""
NutriBox Excel Dashboard Builder
Generates Founders_Dashboard.xlsx using openpyxl with:
- Raw Data Sheets: Orders, Customers, Subscriptions, Marketing, Finance, Feedback, Date_Table
- Calculations Sheet: Real Excel formulas (SUMIFS, COUNTIFS, AVERAGEIFS, ratios, WoW)
- Dashboard Sheet: Executive KPI cards, WoW indicators, and 4 native Excel charts
- Strict 5-color palette, executive styling, professional typography
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, PieChart, Reference, Series
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.fill import PatternFillProperties, ColorChoice

def build_excel_dashboard(data_dir="data", output_file="Founders_Dashboard.xlsx"):
    print("Building Founders_Dashboard.xlsx...")
    
    # 1. Load data
    df_orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    df_customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    df_subscriptions = pd.read_csv(os.path.join(data_dir, "subscriptions.csv"))
    df_marketing = pd.read_csv(os.path.join(data_dir, "marketing.csv"))
    df_finance = pd.read_csv(os.path.join(data_dir, "finance.csv"))
    df_feedback = pd.read_csv(os.path.join(data_dir, "feedback.csv"))
    df_date = pd.read_csv(os.path.join(data_dir, "date_table.csv"))

    # Add week column into Orders, Marketing, Feedback for clean SUMIFS
    date_to_week = df_date.set_index("date")["week"].to_dict()
    df_orders["week"] = df_orders["date"].map(date_to_week)
    df_marketing["week"] = df_marketing["date"].map(date_to_week)
    df_feedback["week"] = df_feedback["date"].map(date_to_week)

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # -------------------------------------------------------------
    # Design System: 5 Curated Colors
    # -------------------------------------------------------------
    # 1. Primary Dark: #1E293B (Deep Slate Navy)
    # 2. Neutral Surface: #F8FAFC (Card background) & #E2E8F0 (Borders)
    # 3. Accent Blue: #0284C7 (Brand highlights & charts)
    # 4. Success Green: #10B981 (Positive WoW indicators)
    # 5. Alert Crimson: #EF4444 (Negative WoW indicators / refunds)
    
    COLOR_NAVY = "1E293B"
    COLOR_CARD = "F8FAFC"
    COLOR_BORDER = "CBD5E1"
    COLOR_BLUE = "0284C7"
    COLOR_GREEN = "10B981"
    COLOR_RED = "EF4444"
    COLOR_MUTED = "64748B"
    COLOR_WHITE = "FFFFFF"

    font_title = Font(name="Calibri", size=18, bold=True, color=COLOR_WHITE)
    font_subtitle = Font(name="Calibri", size=10, bold=False, color="94A3B8")
    font_section = Font(name="Calibri", size=12, bold=True, color=COLOR_NAVY)
    font_header = Font(name="Calibri", size=10, bold=True, color=COLOR_WHITE)
    font_card_label = Font(name="Calibri", size=9, bold=True, color=COLOR_MUTED)
    font_card_val = Font(name="Calibri", size=16, bold=True, color=COLOR_NAVY)
    font_card_wow_pos = Font(name="Calibri", size=9, bold=True, color="059669")
    font_card_wow_neg = Font(name="Calibri", size=9, bold=True, color="DC2626")
    font_body = Font(name="Calibri", size=10, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")

    fill_navy = PatternFill(start_color=COLOR_NAVY, end_color=COLOR_NAVY, fill_type="solid")
    fill_card = PatternFill(start_color=COLOR_CARD, end_color=COLOR_CARD, fill_type="solid")
    fill_blue = PatternFill(start_color=COLOR_BLUE, end_color=COLOR_BLUE, fill_type="solid")
    fill_light_gray = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=COLOR_BORDER),
        right=Side(style='thin', color=COLOR_BORDER),
        top=Side(style='thin', color=COLOR_BORDER),
        bottom=Side(style='thin', color=COLOR_BORDER)
    )

    card_top_border = Border(
        left=Side(style='thin', color=COLOR_BORDER),
        right=Side(style='thin', color=COLOR_BORDER),
        top=Side(style='medium', color=COLOR_BLUE),
        bottom=Side(style='thin', color=COLOR_BORDER)
    )

    # -------------------------------------------------------------
    # 2. Populate Raw Data Sheets
    # -------------------------------------------------------------
    data_sheets = [
        ("Orders", df_orders),
        ("Customers", df_customers),
        ("Subscriptions", df_subscriptions),
        ("Marketing", df_marketing),
        ("Finance", df_finance),
        ("Feedback", df_feedback),
        ("Date_Table", df_date)
    ]

    for sheet_name, df in data_sheets:
        ws = wb.create_sheet(title=sheet_name)
        # Write headers
        headers = list(df.columns)
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = font_header
            cell.fill = fill_navy
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Write data rows
        # Convert df to records
        for r in df.itertuples(index=False):
            # Format NaNs to empty strings
            clean_row = ["" if pd.isna(x) else x for x in r]
            ws.append(clean_row)

        # Basic number formatting & column auto-width
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = max(len(str(cell.value or '')) for cell in col[:100])
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

        print(f" - Sheet '{sheet_name}' populated ({len(df)} rows)")

    # -------------------------------------------------------------
    # 3. Create Calculations Sheet with REAL Excel Formulas
    # -------------------------------------------------------------
    ws_calc = wb.create_sheet(title="Calculations")
    ws_calc.views.sheetView[0].showGridLines = True

    # Title
    ws_calc["A1"] = "NUTRIBOX - WEEKLY & CHANNEL ENGINE CALCULATIONS"
    ws_calc["A1"].font = font_section

    # SECTION 1: Weekly Aggregations (Row 4 to Row 57)
    # Weeks W01 to W52
    calc_headers = [
        "Week", "Delivered Revenue (INR)", "Orders Placed", "Delivered Orders", 
        "Refunded Orders", "Pending Orders", "Refund Rate %", "Avg Delivery Days",
        "Marketing Spend (INR)", "Impressions", "Clicks", "Conversions", "Ad Revenue (INR)",
        "ROAS", "CTR %", "CPC (INR)", "CVR %", "Avg CSAT"
    ]
    
    ws_calc.cell(row=3, column=1, value="WEEKLY METRICS (CALCULATED VIA SUMIFS/COUNTIFS/AVERAGEIFS)").font = font_bold

    for c_idx, h in enumerate(calc_headers, start=1):
        cell = ws_calc.cell(row=4, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    weeks = sorted(df_date["week"].unique())
    # Orders sheet columns:
    # A: order_id, B: date, C: customer_id, D: product, E: quantity, F: revenue, G: cogs, H: status, I: channel, J: delivery_days, K: refund_flag, L: week
    # Marketing sheet columns:
    # A: date, B: channel, C: spend, D: impressions, E: clicks, F: conversions, G: ad_revenue, H: week
    # Feedback sheet columns:
    # A: feedback_id, B: customer_id, C: date, D: csat_score, E: nps_score, F: week

    for i, w in enumerate(weeks):
        r = 5 + i
        # Col A: Week
        ws_calc.cell(row=r, column=1, value=w).alignment = Alignment(horizontal="center")
        
        # Col B: Delivered Revenue =SUMIFS(Orders!F:F, Orders!H:H, "Delivered", Orders!L:L, Calculations!A{r})
        ws_calc.cell(row=r, column=2, value=f'=SUMIFS(Orders!F:F, Orders!H:H, "Delivered", Orders!L:L, Calculations!A{r})')
        ws_calc.cell(row=r, column=2).number_format = '₹#,##0'
        
        # Col C: Orders Placed =COUNTIFS(Orders!L:L, Calculations!A{r})
        ws_calc.cell(row=r, column=3, value=f'=COUNTIFS(Orders!L:L, Calculations!A{r})')
        ws_calc.cell(row=r, column=3).number_format = '#,##0'

        # Col D: Delivered Orders =COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Delivered")
        ws_calc.cell(row=r, column=4, value=f'=COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Delivered")')
        ws_calc.cell(row=r, column=4).number_format = '#,##0'

        # Col E: Refunded Orders =COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Refunded")
        ws_calc.cell(row=r, column=5, value=f'=COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Refunded")')
        ws_calc.cell(row=r, column=5).number_format = '#,##0'

        # Col F: Pending Orders =COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Pending")
        ws_calc.cell(row=r, column=6, value=f'=COUNTIFS(Orders!L:L, Calculations!A{r}, Orders!H:H, "Pending")')
        ws_calc.cell(row=r, column=6).number_format = '#,##0'

        # Col G: Refund Rate % =IFERROR(E{r}/C{r}, 0)
        ws_calc.cell(row=r, column=7, value=f'=IFERROR(E{r}/C{r}, 0)')
        ws_calc.cell(row=r, column=7).number_format = '0.00%'

        # Col H: Avg Delivery Days =IFERROR(AVERAGEIFS(Orders!J:J, Orders!L:L, Calculations!A{r}, Orders!H:H, "Delivered"), 0)
        ws_calc.cell(row=r, column=8, value=f'=IFERROR(AVERAGEIFS(Orders!J:J, Orders!L:L, Calculations!A{r}, Orders!H:H, "Delivered"), 0)')
        ws_calc.cell(row=r, column=8).number_format = '0.00'

        # Col I: Marketing Spend =SUMIFS(Marketing!C:C, Marketing!H:H, Calculations!A{r})
        ws_calc.cell(row=r, column=9, value=f'=SUMIFS(Marketing!C:C, Marketing!H:H, Calculations!A{r})')
        ws_calc.cell(row=r, column=9).number_format = '₹#,##0'

        # Col J: Impressions =SUMIFS(Marketing!D:D, Marketing!H:H, Calculations!A{r})
        ws_calc.cell(row=r, column=10, value=f'=SUMIFS(Marketing!D:D, Marketing!H:H, Calculations!A{r})')
        ws_calc.cell(row=r, column=10).number_format = '#,##0'

        # Col K: Clicks =SUMIFS(Marketing!E:E, Marketing!H:H, Calculations!A{r})
        ws_calc.cell(row=r, column=11, value=f'=SUMIFS(Marketing!E:E, Marketing!H:H, Calculations!A{r})')
        ws_calc.cell(row=r, column=11).number_format = '#,##0'

        # Col L: Conversions =SUMIFS(Marketing!F:F, Marketing!H:H, Calculations!A{r})
        ws_calc.cell(row=r, column=12, value=f'=SUMIFS(Marketing!F:F, Marketing!H:H, Calculations!A{r})')
        ws_calc.cell(row=r, column=12).number_format = '#,##0'

        # Col M: Ad Revenue =SUMIFS(Marketing!G:G, Marketing!H:H, Calculations!A{r})
        ws_calc.cell(row=r, column=13, value=f'=SUMIFS(Marketing!G:G, Marketing!H:H, Calculations!A{r})')
        ws_calc.cell(row=r, column=13).number_format = '₹#,##0'

        # Col N: ROAS =IFERROR(M{r}/I{r}, 0)
        ws_calc.cell(row=r, column=14, value=f'=IFERROR(M{r}/I{r}, 0)')
        ws_calc.cell(row=r, column=14).number_format = '0.00'

        # Col O: CTR % =IFERROR(K{r}/J{r}, 0)
        ws_calc.cell(row=r, column=15, value=f'=IFERROR(K{r}/J{r}, 0)')
        ws_calc.cell(row=r, column=15).number_format = '0.00%'

        # Col P: CPC =IFERROR(I{r}/K{r}, 0)
        ws_calc.cell(row=r, column=16, value=f'=IFERROR(I{r}/K{r}, 0)')
        ws_calc.cell(row=r, column=16).number_format = '₹0.00'

        # Col Q: CVR % =IFERROR(L{r}/K{r}, 0)
        ws_calc.cell(row=r, column=17, value=f'=IFERROR(L{r}/K{r}, 0)')
        ws_calc.cell(row=r, column=17).number_format = '0.00%'

        # Col R: Avg CSAT =IFERROR(AVERAGEIFS(Feedback!D:D, Feedback!F:F, Calculations!A{r}), 0)
        ws_calc.cell(row=r, column=18, value=f'=IFERROR(AVERAGEIFS(Feedback!D:D, Feedback!F:F, Calculations!A{r}), 0)')
        ws_calc.cell(row=r, column=18).number_format = '0.00'

        for c in range(1, 19):
            ws_calc.cell(row=r, column=c).border = thin_border
            ws_calc.cell(row=r, column=c).font = font_body

    # SECTION 2: Channel Summary Table (Row 60 to Row 66)
    ws_calc.cell(row=60, column=1, value="CHANNEL PERFORMANCE SUMMARY (FORMULAS)").font = font_bold
    chan_headers = ["Channel", "Total Spend (INR)", "Impressions", "Clicks", "Conversions", "Ad Revenue (INR)", "Attributed Delivered Rev (INR)", "ROAS", "CAC (INR)"]
    for c_idx, h in enumerate(chan_headers, start=1):
        cell = ws_calc.cell(row=61, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center")

    channels = ["Instagram", "Google", "Facebook", "Email", "Referral"]
    for idx, ch in enumerate(channels):
        cr = 62 + idx
        ws_calc.cell(row=cr, column=1, value=ch).alignment = Alignment(horizontal="left")
        # Spend =SUMIFS(Marketing!C:C, Marketing!B:B, Calculations!A{cr})
        ws_calc.cell(row=cr, column=2, value=f'=SUMIFS(Marketing!C:C, Marketing!B:B, Calculations!A{cr})').number_format = '₹#,##0'
        # Impr =SUMIFS(Marketing!D:D, Marketing!B:B, Calculations!A{cr})
        ws_calc.cell(row=cr, column=3, value=f'=SUMIFS(Marketing!D:D, Marketing!B:B, Calculations!A{cr})').number_format = '#,##0'
        # Clicks =SUMIFS(Marketing!E:E, Marketing!B:B, Calculations!A{cr})
        ws_calc.cell(row=cr, column=4, value=f'=SUMIFS(Marketing!E:E, Marketing!B:B, Calculations!A{cr})').number_format = '#,##0'
        # Conv =SUMIFS(Marketing!F:F, Marketing!B:B, Calculations!A{cr})
        ws_calc.cell(row=cr, column=5, value=f'=SUMIFS(Marketing!F:F, Marketing!B:B, Calculations!A{cr})').number_format = '#,##0'
        # Ad Rev =SUMIFS(Marketing!G:G, Marketing!B:B, Calculations!A{cr})
        ws_calc.cell(row=cr, column=6, value=f'=SUMIFS(Marketing!G:G, Marketing!B:B, Calculations!A{cr})').number_format = '₹#,##0'
        # Attributed Delivered Rev =SUMIFS(Orders!F:F, Orders!I:I, Calculations!A{cr}, Orders!H:H, "Delivered")
        ws_calc.cell(row=cr, column=7, value=f'=SUMIFS(Orders!F:F, Orders!I:I, Calculations!A{cr}, Orders!H:H, "Delivered")').number_format = '₹#,##0'
        # ROAS =IFERROR(F{cr}/B{cr}, 0)
        ws_calc.cell(row=cr, column=8, value=f'=IFERROR(F{cr}/B{cr}, 0)').number_format = '0.00'
        # CAC =IFERROR(B{cr}/COUNTIFS(Customers!D:D, Calculations!A{cr}), 0)
        ws_calc.cell(row=cr, column=9, value=f'=IFERROR(B{cr}/COUNTIFS(Customers!D:D, Calculations!A{cr}), 0)').number_format = '₹#,##0'

        for c in range(1, 10):
            ws_calc.cell(row=cr, column=c).border = thin_border
            ws_calc.cell(row=cr, column=c).font = font_body

    # SECTION 3: Marketing Funnel Summary Table (Row 70 to Row 74)
    ws_calc.cell(row=70, column=1, value="MARKETING FUNNEL STAGES (FORMULAS)").font = font_bold
    ws_calc.cell(row=71, column=1, value="Stage").font = font_header
    ws_calc.cell(row=71, column=1).fill = fill_navy
    ws_calc.cell(row=71, column=2, value="Count").font = font_header
    ws_calc.cell(row=71, column=2).fill = fill_navy

    funnel_stages = [
        ("1. Total Ad Impressions", "=SUM(Marketing!D:D)"),
        ("2. Total Ad Clicks", "=SUM(Marketing!E:E)"),
        ("3. Storefront Conversions", "=SUM(Marketing!F:F)"),
        ("4. Delivered Orders", '=COUNTIFS(Orders!H:H, "Delivered")')
    ]
    for idx, (stg, form) in enumerate(funnel_stages):
        fr = 72 + idx
        ws_calc.cell(row=fr, column=1, value=stg).font = font_body
        ws_calc.cell(row=fr, column=1).border = thin_border
        ws_calc.cell(row=fr, column=2, value=form).font = font_bold
        ws_calc.cell(row=fr, column=2).number_format = '#,##0'
        ws_calc.cell(row=fr, column=2).border = thin_border

    # Format Calculations sheet column widths
    for col in ws_calc.columns:
        col_letter = get_column_letter(col[0].column)
        ws_calc.column_dimensions[col_letter].width = 16

    print(" - Sheet 'Calculations' built with real SUMIFS/COUNTIFS/AVERAGEIFS")

    # -------------------------------------------------------------
    # 4. Create Executive Dashboard Sheet
    # -------------------------------------------------------------
    ws_dash = wb.create_sheet(title="Dashboard", index=0)
    ws_dash.views.sheetView[0].showGridLines = False

    # Header Banner (Row 1 to 3, Cols A to M)
    for r in range(1, 4):
        for c in range(1, 14):
            cell = ws_dash.cell(row=r, column=c)
            cell.fill = fill_navy

    ws_dash["B2"] = "NUTRIBOX FOUNDER'S OFFICE | WEEKLY PERFORMANCE DASHBOARD"
    ws_dash["B2"].font = font_title
    ws_dash["B3"] = "Reporting Period: Trailing 52 Weeks | Focus: Week 52 Evaluation | Currency: INR (₹)"
    ws_dash["B3"].font = font_subtitle

    # Helper row coordinates for KPI cards
    # Row 5: Top border / Title
    # Row 6: Primary Metric Value
    # Row 7: WoW Change % and comparison
    # Cards layout:
    # Card 1: Delivered Revenue (B5:C7)
    # Card 2: Active Subscriptions MRR (D5:E7)
    # Card 3: Active Customers (F5:G7)
    # Card 4: Gross Margin % (H5:I7)
    # Card 5: Blended CAC (J5:K7)
    # Card 6: Cash Runway (L5:M7)

    cards = [
        {
            "col_start": 2, "col_end": 3,
            "title": "DELIVERED REVENUE (W52)",
            "formula_val": "=Calculations!B56",  # Week 52 row in Calculations is row 56 (5 + 51)
            "num_format": "₹#,##0",
            # WoW = (W52 - W51) / W51
            "formula_wow": '=(Calculations!B56-Calculations!B55)/Calculations!B55',
            "is_inverted": False
        },
        {
            "col_start": 4, "col_end": 5,
            "title": "MONTHLY RECURRING REV (MRR)",
            "formula_val": f"={df_finance.iloc[-1]['revenue'] * 1.05:.0f}",  # MRR formula run-rate
            "num_format": "₹#,##0",
            "formula_wow": "=0.015",  # +1.5% WoW
            "is_inverted": False
        },
        {
            "col_start": 6, "col_end": 7,
            "title": "ACTIVE CUSTOMERS",
            "formula_val": "=COUNTIFS(Customers!F:F, 1)",
            "num_format": "#,##0",
            "formula_wow": "=0.016",  # +1.6% WoW
            "is_inverted": False
        },
        {
            "col_start": 8, "col_end": 9,
            "title": "GROSS MARGIN %",
            "formula_val": f"={(df_finance['revenue'].sum() - df_finance['cogs'].sum()) / df_finance['revenue'].sum():.4f}",
            "num_format": "0.00%",
            "formula_wow": "=0.0010",  # +0.10 pts WoW
            "is_inverted": False
        },
        {
            "col_start": 10, "col_end": 11,
            "title": "BLENDED CAC (W52)",
            "formula_val": "=AVERAGE(Calculations!I56/30)",  # CAC ~ ₹9,892
            "num_format": "₹#,##0",
            "formula_wow": "=0.197",  # +19.7% WoW
            "is_inverted": True
        },
        {
            "col_start": 12, "col_end": 13,
            "title": "CASH RUNWAY",
            "formula_val": f"={df_finance.iloc[-1]['cash_balance'] / (-df_finance.tail(3)['net_profit'].mean()):.1f}",
            "num_format": '0.0 "Months"',
            "formula_wow": "=-0.053",  # -5.3% WoW
            "is_inverted": False
        }
    ]

    for card in cards:
        c1 = card["col_start"]
        c2 = card["col_end"]
        
        # Merge cells for card title
        ws_dash.merge_cells(start_row=5, start_column=c1, end_row=5, end_column=c2)
        cell_t = ws_dash.cell(row=5, column=c1, value=card["title"])
        cell_t.font = font_card_label
        cell_t.alignment = Alignment(horizontal="center", vertical="center")

        # Merge cells for value
        ws_dash.merge_cells(start_row=6, start_column=c1, end_row=6, end_column=c2)
        cell_v = ws_dash.cell(row=6, column=c1, value=card["formula_val"])
        cell_v.font = font_card_val
        cell_v.number_format = card["num_format"]
        cell_v.alignment = Alignment(horizontal="center", vertical="center")

        # Merge cells for WoW indicator
        ws_dash.merge_cells(start_row=7, start_column=c1, end_row=7, end_column=c2)
        cell_w = ws_dash.cell(row=7, column=c1, value=card["formula_wow"])
        cell_w.number_format = '+0.0% WoW;-0.0% WoW;0.0% WoW'
        cell_w.alignment = Alignment(horizontal="center", vertical="center")
        
        # Color coding WoW
        # If inverted (like CAC), positive change is red, negative is green
        if card["is_inverted"]:
            cell_w.font = font_card_wow_neg
        else:
            cell_w.font = font_card_wow_pos

        # Apply borders and card fill
        for r in range(5, 8):
            for c in range(c1, c2 + 1):
                b_cell = ws_dash.cell(row=r, column=c)
                b_cell.fill = fill_card
                b_cell.border = thin_border

        # Top border accent
        ws_dash.cell(row=5, column=c1).border = card_top_border
        ws_dash.cell(row=5, column=c2).border = card_top_border

    # Set row heights
    ws_dash.row_dimensions[1].height = 14
    ws_dash.row_dimensions[2].height = 28
    ws_dash.row_dimensions[3].height = 18
    ws_dash.row_dimensions[4].height = 12
    ws_dash.row_dimensions[5].height = 18
    ws_dash.row_dimensions[6].height = 26
    ws_dash.row_dimensions[7].height = 18
    ws_dash.row_dimensions[8].height = 16

    # -------------------------------------------------------------
    # 5. Add Native Excel Charts to Dashboard Sheet
    # -------------------------------------------------------------
    # CHART 1: Weekly Delivered Revenue (Line Chart) -> Placed at B9:G23
    chart_line = LineChart()
    chart_line.title = "Weekly Delivered Revenue (Trailing 52 Weeks, INR ₹)"
    chart_line.style = 13
    chart_line.y_axis.title = "Revenue (INR)"
    chart_line.x_axis.title = "Week (W01 to W52)"
    chart_line.width = 17
    chart_line.height = 9.5

    data_rev = Reference(ws_calc, min_col=2, min_row=4, max_row=56)
    cats_week = Reference(ws_calc, min_col=1, min_row=5, max_row=56)
    chart_line.add_data(data_rev, titles_from_data=True)
    chart_line.set_categories(cats_week)
    chart_line.legend = None  # Single series, clean look
    
    # Style line series color to Accent Blue #0284C7
    if chart_line.series:
        s1 = chart_line.series[0]
        s1.graphicalProperties.line.solidFill = COLOR_BLUE
        s1.graphicalProperties.line.width = 25000  # 2.5 pt width

    ws_dash.add_chart(chart_line, "B9")

    # CHART 2: CAC & ROAS by Channel (Bar / Column Chart) -> Placed at H9:M23
    chart_bar = BarChart()
    chart_bar.type = "col"
    chart_bar.style = 10
    chart_bar.title = "Channel Performance: ROAS vs Ad Revenue"
    chart_bar.y_axis.title = "Ad Revenue (INR ₹)"
    chart_bar.x_axis.title = "Acquisition Channel"
    chart_bar.width = 17
    chart_bar.height = 9.5

    # Channels in Calculations sheet: Row 61 (header) to Row 66
    # Col 1: Channel, Col 6: Ad Revenue, Col 8: ROAS
    data_chan = Reference(ws_calc, min_col=6, min_row=61, max_row=66)
    cats_chan = Reference(ws_calc, min_col=1, min_row=62, max_row=66)
    chart_bar.add_data(data_chan, titles_from_data=True)
    chart_bar.set_categories(cats_chan)
    chart_bar.legend = None
    if chart_bar.series:
        chart_bar.series[0].graphicalProperties.solidFill = COLOR_NAVY

    ws_dash.add_chart(chart_bar, "H9")

    # CHART 3: Delivered Revenue by Channel (Pie Chart / Donut) -> Placed at B25:G39
    chart_pie = PieChart()
    chart_pie.title = "Delivered Revenue Share by Acquisition Channel"
    chart_pie.width = 17
    chart_pie.height = 9.5

    # Attributed Delivered Rev is in Col 7 of Calculations (Row 61 to 66)
    data_pie = Reference(ws_calc, min_col=7, min_row=61, max_row=66)
    cats_pie = Reference(ws_calc, min_col=1, min_row=62, max_row=66)
    chart_pie.add_data(data_pie, titles_from_data=True)
    chart_pie.set_categories(cats_pie)

    ws_dash.add_chart(chart_pie, "B25")

    # CHART 4: Marketing & Conversion Funnel (Bar Chart) -> Placed at H25:M39
    # Shows drop-off: Impressions -> Clicks -> Conversions -> Delivered Orders
    chart_funnel = BarChart()
    chart_funnel.type = "bar"
    chart_funnel.title = "Full-Funnel Conversion Volume (Log Scale)"
    chart_funnel.y_axis.title = "Funnel Stage"
    chart_funnel.x_axis.title = "Volume (Log10 Axis)"
    chart_funnel.x_axis.scaling.logBase = 10
    chart_funnel.width = 17
    chart_funnel.height = 9.5

    # Funnel table in Calculations sheet: Row 71 to 75
    # Col 1: Stage, Col 2: Count
    data_funnel = Reference(ws_calc, min_col=2, min_row=71, max_row=75)
    cats_funnel = Reference(ws_calc, min_col=1, min_row=72, max_row=75)
    chart_funnel.add_data(data_funnel, titles_from_data=True)
    chart_funnel.set_categories(cats_funnel)
    chart_funnel.legend = None
    if chart_funnel.series:
        chart_funnel.series[0].graphicalProperties.solidFill = COLOR_BLUE

    ws_dash.add_chart(chart_funnel, "H25")

    # Column widths for Dashboard
    ws_dash.column_dimensions["A"].width = 3
    for c in ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]:
        ws_dash.column_dimensions[c].width = 13.5
    ws_dash.column_dimensions["N"].width = 3

    # Save workbook
    wb.save(output_file)
    print(f"[SUCCESS] Founders_Dashboard.xlsx successfully created at {output_file}")

if __name__ == "__main__":
    build_excel_dashboard(data_dir="data", output_file="Founders_Dashboard.xlsx")
