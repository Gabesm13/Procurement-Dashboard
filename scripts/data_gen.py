#!/usr/bin/env python3
"""
Generate synthetic data for the Procurement Dashboard
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path

def main(seed: int):
    # Fix randomness
    np.random.seed(seed)

    # Locate (and create) the data output folder
    project_root = Path(__file__).resolve().parent
    out_dir = project_root / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. TOP-LEVEL KPIs
# -----------------------------------------------------------------------------

    kpis = {
        "cost_of_material": 10556,
        "pct_change_material": -54.90,
        "cost_of_avoidance": 6279,
        "pct_change_avoidance": -54.42,
        "savings": 16976,
        "pct_change_savings": -55.50
    }

    with open(out_dir / "procurement_kpis.json", "w") as f:
        json.dump(kpis, f, indent=2)

# -----------------------------------------------------------------------------
# 2. SAVINGS BY DEPARTMENT (NON-STACKED BAR CHART) TOTALS
# -----------------------------------------------------------------------------

    savings_df = pd.DataFrame({
        "Department": [
            "Transmissions",
            "Sensors",
            "Other",
            "Machine",
            "Forklift",
            "Batteries",
        ],
        "Savings": [
            97465,
            84101,
            90986,
            88876,
            85327,
            102533,
        ],
    })

    savings_df.to_csv(out_dir / "savings_by_department.csv", index=False)

# -----------------------------------------------------------------------------
# 3. MONTHLY SAVINGS BY DEPARTMENT (STACKED BAR CHART)
# -----------------------------------------------------------------------------

    dept_order = [
        "Transmissions",
        "Sensors",
        "Other",
        "Machine",
        "Forklift",
        "Batteries",
    ]

    monthly_data = {
        "Mar 2022": {"Transmissions": 1902, "Sensors": 2975, "Other": 3468, "Machine": 6205, "Forklift": 4406,
                       "Batteries": 1405},
        "Apr 2022": {"Transmissions": 6261, "Sensors": 10495, "Other": 4046, "Machine": 6284, "Forklift": 6446,
                       "Batteries": 5231},
        "May 2022": {"Transmissions": 13257, "Sensors": 2827, "Other": 10726, "Machine": 6753, "Forklift": 7032,
                     "Batteries": 10240},
        "Jun 2022": {"Transmissions": 4383, "Sensors": 5990, "Other": 8505, "Machine": 8041, "Forklift": 8872,
                      "Batteries": 10572},
        "Jul 2022": {"Transmissions": 11684, "Sensors": 11022, "Other": 7536, "Machine": 8935, "Forklift": 5728,
                      "Batteries": 11509},
        "Aug 2022": {"Transmissions": 7680, "Sensors": 8429, "Other": 6317, "Machine": 6491, "Forklift": 4994,
                        "Batteries": 7167},
        "Sep 2022": {"Transmissions": 9415, "Sensors": 5890, "Other": 8829, "Machine": 9450, "Forklift": 7755,
                           "Batteries": 6492},
        "Oct 2022": {"Transmissions": 5858, "Sensors": 12772, "Other": 7769, "Machine": 6415, "Forklift": 7677,
                         "Batteries": 13641},
        "Nov 2022": {"Transmissions": 11993, "Sensors": 5290, "Other": 9131, "Machine": 6481, "Forklift": 4274,
                          "Batteries": 9542},
        "Dec 2022": {"Transmissions": 2829, "Sensors": 5479, "Other": 5896, "Machine": 6085, "Forklift": 9988,
                          "Batteries": 10750},
        "Jan 2023": {"Transmissions": 11413, "Sensors": 3471, "Other": 8423, "Machine": 9068, "Forklift": 8813,
                         "Batteries": 7026},
        "Feb 2023": {"Transmissions": 8750, "Sensors": 7140, "Other": 3964, "Machine": 4200, "Forklift": 7050,
                          "Batteries": 7495},
        "Mar 2023": {"Transmissions": 2040, "Sensors": 2321, "Other": 6376, "Machine": 4468, "Forklift": 2292,
                       "Batteries": 1463},
    }

    records = []
    for month_year, depts in monthly_data.items():
        for dept in dept_order:
            records.append({
                "MonthYear": month_year,
                "Department": dept,
                "Savings": depts[dept],
            })

    monthly_df = pd.DataFrame(records)
    monthly_df.to_csv(
        out_dir / "monthly_savings_by_department.csv",
        index=False,
    )

# -----------------------------------------------------------------------------
# 4a. PROCUREMENT ROI (MAR 2022 - MAR 2023)
# -----------------------------------------------------------------------------

    roi_months = [
        "Mar 2022", "Apr 2022", "May 2022", "Jun 2022", "Jul 2022",
        "Aug 2022", "Sep 2022", "Oct 2022", "Nov 2022", "Dec 2022",
        "Jan 2023", "Feb 2023", "Mar 2023",
    ]
    roi_values = [
        15100, 25000, 35000, 28000, 36000,
        25300, 29000, 37000, 29000, 28500,
        28700, 24800, 12000,
    ]

    roi_df = pd.DataFrame({
        "Month": roi_months,
        "Procurement ROI": roi_values,
    })
    roi_df.to_csv(out_dir / "procurement_roi.csv", index=False)

# -----------------------------------------------------------------------------
# 4b. ROI FORECAST (APR 2023 - SEP 2023)
# -----------------------------------------------------------------------------

    forecast_months = ["Apr 2023", "May 2023", "Jun 2023", "Jul 2023", "Aug 2023", "Sep 2023"]
    forecast_values = [21000, 22000, 18800, 23000, 16000, 13500]

    forecast_df = pd.DataFrame({
        "Month": forecast_months,
        "Forecast": forecast_values,
    })
    forecast_df.to_csv(out_dir / "procurement_forecast.csv", index=False)

    print("Data generation complete. Files saved in 'data/' directory:")
    print("- procurement_kpis.json")
    print("- savings_by_department.csv")
    print("- monthly_savings_by_department.csv")
    print("- procurement_roi.csv")
    print("- procurement_forecast.csv")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate data for the Procurement Dashboard"
    )
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    args = parser.parse_args()
    main(args.seed)