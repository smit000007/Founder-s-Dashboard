"""
Root execution wrapper for build_excel_dashboard.py
Allows running 'python build_excel_dashboard.py' directly from the root workspace folder.
"""
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(base_dir, "founders-dashboard")

if sub_dir not in sys.path:
    sys.path.insert(0, sub_dir)

from build_excel_dashboard import build_excel_dashboard

if __name__ == "__main__":
    data_dir = os.path.join(sub_dir, "data") if os.path.exists(os.path.join(sub_dir, "data")) else os.path.join(base_dir, "data")
    output_file = os.path.join(sub_dir, "Founders_Dashboard.xlsx")
    build_excel_dashboard(data_dir=data_dir, output_file=output_file)
    print(f"\n[OK] Excel Dashboard ready: {output_file}")
