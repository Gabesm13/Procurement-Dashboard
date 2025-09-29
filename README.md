# PROCUREMENT DASHBOARD (PYTHON + PLOTLY)

Generates an interactive procurement KPI dashboard as a single HTML file using synthetic example data. Visualizes cost of material, cost of avoidance, total savings, monthly savings by department, and procurement ROI with a simple forecast.

Tech:
Python 3.10+; NumPy, Pandas, Plotly

Quickstart:
# 1) Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip

# 2) Install dependencies
pip install -r requirements.txt

# 3) Generate synthetic data -> data/
python scripts/data_gen.py --seed 42

# 4) Build the dashboard -> outputs/dashboard.html
python scripts/viz.py

# 5) Open in your browser (macOS)
open outputs/dashboard.html

Project structure:
scripts/
  data_gen.py      # creates JSON/CSV inputs in /data
  viz.py           # builds the HTML dashboard in /outputs
data/              # generated data files (JSON/CSV)
outputs/           # generated dashboard.html
requirements.txt   # dependencies
README.md          # this file

Notes:
All numbers are synthetic and for demonstration only.

License:
MIT
