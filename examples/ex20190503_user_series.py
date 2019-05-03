"""
Example of working with a user-defined series.

This example does not make much sense on its own, as the calculation should really be moved to
another library code. However, this shows the workflow.

"""

from myplatform import fetch, quick_plot, Providers


#---------------------------------------------------------------------------------------
# Normally, the user-defined series would be handled in a library. Kept here to keep
# Example self-contained.

def us_inflation(query_ticker):
    if not query_ticker == 'US_CPI_INFLATION':
        raise ValueError('Wrong series!')
    cpi_index = fetch('F@CPIAUCSL') # All -items, SA
    inf = cpi_index.pct_change(12)
    return inf
# Push the handler into the UserProvider
# Assume we are still using the default provider code
user_provider = Providers['U']
user_provider.SeriesMapper['US_CPI_INFLATION'] = us_inflation
# End of code that should be in a library.
#--------------------------------------------------------------------


# Now we can fetch it.
# Note that since this calculated series uses the US CPI index level, the system
# automatically also creates the CPI series on the database when this is called.
inf = fetch('U@US_CPI_INFLATION')
quick_plot(inf)