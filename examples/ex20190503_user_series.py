"""
Example of working with a user-defined series.

This example does not make much sense on its own, as the calculation should really be moved to
another library code. However, this shows the workflow.

"""


from econ_platform_core import fetch, Providers
from econ_platform.start import quick_plot


#---------------------------------------------------------------------------------------
# Normally, the user-defined series would be handled in a library. Kept here to keep
# Example self-contained.

def us_inflation(series_meta):
    """

    :param series_meta: econ_platform_core.SeriesMetadata
    :return:
    """
    if not str(series_meta.ticker_query) == 'US_CPI_INFLATION':
        raise ValueError('Wrong series!')
    cpi_index = fetch('F@CPIAUCSL') # All -items, SA
    inf = cpi_index.pct_change(12)
    series_meta.series_name = '12-month Change in U.S. CPI Inflation'
    series_meta.series_description = 'Calculated series'
    return inf
# Push the handler into the UserProvider
user_provider = Providers.UserProvider
user_provider.SeriesMapper['US_CPI_INFLATION'] = us_inflation
# End of code that should be in a library.
#--------------------------------------------------------------------


# Now we can fetch it.
# Note that since this calculated series uses the US CPI index level, the system
# automatically also creates the CPI series on the database when this is called.
inf = fetch('U@US_CPI_INFLATION')
quick_plot(inf)