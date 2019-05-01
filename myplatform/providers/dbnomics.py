"""
dbnomics.py

Functions to fetch data from DBNomics, and convert to standard format.

In this case, convert pandas data frames into a list of time series.


The challenge for our purposes is coming up with a common interface for the more advanced queries
the DBnmonics interface supports.

Examples taken from the dnomics package __init__.py:
   - fetch one series:
      fetch_series("AMECO/ZUTN/EA19.1.0.0.0.ZUTN")

    - fetch all the series of a dataset:
      fetch_series("AMECO", "ZUTN")

    - fetch many series from different datasets:
      fetch_series(["AMECO/ZUTN/EA19.1.0.0.0.ZUTN", "AMECO/ZUTN/DNK.1.0.0.0.ZUTN", "IMF/CPI/A.AT.PCPIT_IX"])

    - fetch many series from the same dataset, searching by dimension:
      fetch_series("AMECO", "ZUTN", dimensions={"geo": ["dnk"]})

    - fetch many series from the same dataset, searching by code mask:
      fetch_series("IMF", "CPI", series_code="M.FR+DE.PCPIEC_WT")

For now, will just support a list of series. Will need to look at how to come up with a common interface
for "table queries" across providers.


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

import dbnomics




