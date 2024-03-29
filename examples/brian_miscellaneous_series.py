
"""
Brian Romanchuk's miscellaneous series. Used in example code.


To use this file, point
[Options]
miscellaneous_series_module=<path to this file>

However, it makes more sense to create your own file, and use any series from here that you like.

Copyright 2019 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import pandas
import econ_platform


def calc_fed(series_meta):
    """
    Splice together a daily Fed Funds rate from FRED series.

    :param series_meta: econ_platform_core.SeriesMetadata
    :return:
    """
    # Just use series_meta to fill in description
    effective = econ_platform.fetch('F@DFF')
    target = econ_platform.fetch('F@DFEDTAR')
    upper = econ_platform.fetch('F@DFEDTARU')
    downer = econ_platform.fetch('F@DFEDTARL')
    new_target = (upper + downer)/2.
    out = target.combine_first(new_target)
    cut_off = out.index[0]
    out = out.combine_first(effective[:cut_off])
    out.name = 'FedFunds: Long Series'
    series_meta.series_description= 'Combination of Fed Funds (FF) Effect (up to 1982), FF target (to 2008), ' \
                                    'then average of upper and lower bounds. '
    series_meta.series_name = 'Fed Funds Long Time History'
    return out, series_meta


def us_inflation_dispersion(series_meta, fn_args):
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
        cpi_index = econ_platform.fetch('F@CPIAUCSL') # All -items, SA
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
        level = econ_platform.fetch('F@'+group)
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



SeriesDict = {
    'FedFunds': calc_fed,
}

FunctionDict = {
    'US_INF_DISPERSION': us_inflation_dispersion,
}




