"""
hello_world.py

Minimal econ_platform example.

Note: Will not run "out of the box"; need to install dependencies, mainly Pandas, DB.nomics, and matplotlib...
"""

# Step 0: Overhead; need to import the package, and initialise it.
# (Using econ_platform.start forces the initialisation step.)
from econ_platform.start import fetch, quick_plot

# Step 1: Fetch input data - Iceland HICP Inflation (Monthly)
level = fetch('D@Eurostat/prc_hicp_midx/M.I05.CP00.IS')

# Step 2: Highly complex quantitative stuff!
inflation_rate = 100.*level.pct_change(12)

# Step 3: Output.
quick_plot(inflation_rate, title='Iceland HICP Inflation')