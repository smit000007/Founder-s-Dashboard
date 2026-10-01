"""
Root execution wrapper for generate_data.py
Allows running 'python generate_data.py' directly from the root workspace folder.
"""
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(base_dir, "founders-dashboard")

if sub_dir not in sys.path:
    sys.path.insert(0, sub_dir)

from generate_data import generate_all_data

if __name__ == "__main__":
    output_dir = os.path.join(sub_dir, "data")
    generate_all_data(output_dir=output_dir, seed=42)
