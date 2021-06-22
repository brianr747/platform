"""
Example of working with a user-defined "functional" series

This example does not make much sense on its own, as the calculation should really be moved to
another library code. However, this shows the workflow.

"""

import pandas

from econ_platform_core import fetch, Providers, reset_update_time
from econ_platform.start import quick_plot


#---------------------------------------------------------------------------------------
# Normally, the user-defined series would be handled in a library. Kept here to keep
# Example self-contained.

def inflation_fn(series_meta, fn_args):
    """
    Inflation dispersion in the U.S., based on major groups
    food and beverages, housing, apparel, transportation, medical care, recreation, education and communication, and other goods and services

    fn_args must be of the form N, return_type
    N = # of months to do the analysis on (annualised inflation rate over N months).
    return_type = "headline", "min", "max"  (case insensitive, do not include quotes).
            Either returns the headline inflation rate, or the min or max of the major groups.

    :param series_meta: econ_platform_core.SeriesMetadata
    :param fn_args': str
    :return:
    """

    try:
        N_months, return_type = fn_args.split(',')
    except:
        raise ValueError('Dispersion function has two arguments: N, return_type')
    # Remove any quotes from people who don't follow directions...
    return_type = return_type.replace("'", '')
    return_type = return_type.replace('"', '')
    return_type = return_type.strip()
    return_type = return_type.upper()
    try:
        N_months = int(N_months)
    except:
        raise ValueError('N_months must be an integer')
    if return_type not in ('HEADLINE', 'MIN', 'MAX'):
        raise ValueError(f'Invalid return type {return_type}, must be one of HEADLINE, MIN, MAX')
    if return_type == 'HEADLINE':
        cpi_index = fetch('F@CPIAUCSL') # All -items, SA
        pct_chg = cpi_index.pct_change(N_months)
        factor = 1. + pct_chg
        annualised = pow(factor, 12./float(N_months))
        annualised = 100.*(annualised - 1.)
        annualised.name = str(series_meta.ticker_full)
        series_meta.series_name = 'N-month Annualised Change in U.S. CPI Inflation'
        series_meta.series_description = 'Calculated series'
        return annualised
    # Groups:
    # food and beverages, housing, apparel, transportation, medical care, recreation, education and communication, and other goods and services
    groups_tickers = ['CPIFABSL', 'CPIHOSSL', 'CPIAPPSL', 'CPITRNSL', 'CPIMEDSL', 'CPIRECSL',
                      'CPIEDUSL', 'CPIOGSSL']

    group_df = pandas.DataFrame()
    for group in groups_tickers:
        level = fetch('F@'+group)
        pct_chg = level.pct_change(N_months)
        factor = 1. + pct_chg
        annualised = pow(factor, 12./float(N_months))
        annualised = 100.*(annualised - 1.)
        group_df[group] = annualised
    group_df.dropna(axis=0, inplace=True)
    if return_type == 'MIN':
        out = group_df.min(axis=1)
        series_meta.series_name = f'Minimum {N_months}-annualised inflation for major groups in U.S.'
    else:
        out = group_df.max(axis=1)
        series_meta.series_name = f'Maximum {N_months}-annualised inflation for major groups in U.S.'
    series_meta.series_description = 'Calculated series'
    return out, series_meta

# Push the handler into the UserProvider
user_provider = Providers.UserProvider
user_provider.FunctionMapper['US_INF_DISPERSION'] = inflation_fn
# End of code that should be in a library.
#--------------------------------------------------------------------


# Now we can fetch it.
# Note that since this calculated series uses the US CPI index level, the system
# automatically also creates the CPI series on the database when this is called.

# Call reset_update_time() to force an update of the series while the code is under development.
# Note that this does not affect the series fetched from the external provider.
reset_update_time('U@US_INF_DISPERSION(24, MAX)')
inf = fetch('U@US_INF_DISPERSION(24, MAX)')


quick_plot(inf)