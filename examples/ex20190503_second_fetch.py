"""
Plot the 10-year US Treasury/Euro area AAA govvie  spread in 4 -- count'em, 4 -- lines of code.
(Couldn't find a daily bund series...)
"""

from econ_platform.start import fetch, quick_plot
# from econ_platform.analysis.quick_plot import quick_plot

ust10 = fetch('F@DGS10')
euro_AAA_10 = fetch('D@Eurostat/irt_euryld_d/D.EA.PYC_RT.Y10.CGB_EA_AAA')
quick_plot(ust10-euro_AAA_10, title='U.S. 10Y Spread Over AAA-Rated Euro Govvie')