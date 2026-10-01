"""
Root execution wrapper for kpi_calculations.py
Allows running 'python kpi_calculations.py' directly from the root workspace folder.
"""
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(base_dir, "founders-dashboard")

if sub_dir not in sys.path:
    sys.path.insert(0, sub_dir)

from kpi_calculations import compute_kpis

if __name__ == "__main__":
    data_dir = os.path.join(sub_dir, "data") if os.path.exists(os.path.join(sub_dir, "data")) else os.path.join(base_dir, "data")
    compute_kpis(data_dir=data_dir)
