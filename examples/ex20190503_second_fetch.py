"""
Plot the 10-year US Treasury/Euro area AAA govvie  spread in 4 -- count'em, 4 -- lines of code.
(Couldn't find a daily bund series...)
"""

from econ_platform.start import fetch, quick_plot

ust10 = fetch('F@DGS10')
euro_AAA_10 = fetch('D@Eurostat/irt_h_euryld_d/D.PAR.Y10.EA')
quick_plot(100*(ust10-euro_AAA_10), title='U.S. 10Y Spread Over Euro Govvie')