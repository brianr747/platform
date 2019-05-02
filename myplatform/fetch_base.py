"""

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
import os.path
import pandas
import logging

import myplatform.utils as utils
from myplatform import log
import myplatform.providers.provider_dbnomics as provider_dbnomics

def fetch(ticker, database='SQL', dropna=True):
    """
    Fetch a series from database; may create series and/or update as needed.

    :param ticker: str
    :param database: str
    :param dropna: bool
    :param always_list: bool
    :return: pandas.Series
    """
    # NOTE: This will get fancier, but don't over-design for now...
    if not database=='TEXT':
        raise NotImplementedError('Only the text database supported!')
    source_code, source_ticker = utils.split_ticker_information(ticker)
    if not source_code == 'D':
        raise NotImplementedError('Only DBnomics (D) supported for now...')
    filename = utils.convert_ticker_to_variable(ticker) + '.txt'
    full_name = os.path.join(os.path.dirname(__file__), 'text_database', filename)
    if os.path.exists(full_name):
        # Load the file...
        log('loading from %s', full_name)
        df = pandas.read_csv(filepath_or_buffer=full_name, sep='\t', parse_dates=True, index_col=0)
        ser = pandas.Series(df[df.columns[0]])
        return ser
    else:
        log('Fetching %s', ticker)
        ser_list = provider_dbnomics.fetch(source_ticker)
        if dropna:
            ser_list = [x.dropna() for x in ser_list]
        log('Writing to %s', full_name)
        for x in ser_list:
            x.to_csv(path_or_buf=full_name, sep='\t', header=True)
    if len(ser_list) > 1:
        logging.error('Should not have fetches that return multiple series...')

    return ser_list[0]




