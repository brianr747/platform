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
import myplatform.databases as databases

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
    database_manager = databases.Databases[database]
    source_code, source_ticker = utils.split_ticker_information(ticker)
    if not source_code == 'D':
        raise NotImplementedError('Only DBnomics (D) supported for now...')

    if database_manager.Exists(ticker):
        # Load the file...
        return database_manager.Retrieve(ticker)
    else:
        log('Fetching %s', ticker)
        ser_list = provider_dbnomics.fetch(source_ticker)
        if dropna:
            ser_list = [x.dropna() for x in ser_list]
        if len(ser_list) > 1:
            raise NotImplementedError('More than one series in a fetch not supported')
        log('Writing %s', ticker)
        for x in ser_list:
            database_manager.Write(x, x.name)
    return ser_list[0]




