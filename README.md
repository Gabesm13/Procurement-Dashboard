PROCUREMENT DASHBOARD (PYTHON + PLOTLY)

A small, self-contained project that generates an interactive Procurement KPI dashboard as a single HTML file.
It uses synthetic example data to visualize: cost of material, cost of avoidance, total savings, monthly savings by department,
and procurement ROI with a simple forecast.

Tech:
Python 3.10+; NumPy, Pandas, Plotly

Quickstart:
# optional: create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# install dependencies
pip install numpy pandas plotly

# 1) generate synthetic data -> data/
python scripts/data_gen.py --seed 42

# 2) build the dashboard -> outputs/dashboard.html
python scripts/viz.py

# open the result in your browser
open outputs/dashboard.html

Project structure:
scripts/data_gen.py   - creates JSON/CSV inputs
scripts/viz.py        - builds the HTML dashboard
data/                 - generated data files
outputs/              - generated dashboard.html

Notes:
All numbers are synthetic and for demonstration only.
Feel free to adapt the code and data schema for real datasets.

License:
MIT
