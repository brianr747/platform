# TODO List

## Introduction

This file is not in any sense organised. I am just throwing lists of features
that would be useful, without worrying about their priority.

Not including some of the major refactoring things that are part of the design 
document.

# Point Form Items

Stuff that can be summarised easily.

- Refactor code to use the *tickers.py* module. Eiminate ambiguity about what a ticker
string represents.
- Add "series name"/"series description" as fields that exist for all series. 
Should do quickly, as every provider has to support this!
- EViews support.
- Bloomberg API.
- local tickers. (Friendly tickers defined by users.)
- data type tickers. For example "IBM|dividend" to get the dividend for "IBM."
- Provider-specific meta-data.
- The *fetch()* command needs to ensure uniformity of dates coming from external
providers. 
- Create config settings to bave default database per provider (e.g., certain commercial providers only allow data to go to a particular machine, so that data goes to SQLite).

# Update Protocol

The current system looks a bit silly; what we need is a dynamic update during
the *fetch()* processing. (At the time of writing, if the series exists on the 
database, it is not updated at all.) I can live without that feature for now
(I know that I just need to delete the appropriate text file), but others will 
not be happy with it. (Worst case, they will short-circuit the fetch, and send
every *fetch()* to external providers, which is exactly what I am trying to avoid.)

Once my SQL code is more stable, I will work on this protocol.

# Support Tables

Create a simple database front end so that data can be easily stored in a "table"
(probably a SQL database, but could be a delimited text file). This will be very useful
for the CANSIM_CSV and ABS_XLS providers as they have a boatload of series, but most
users will not want to import all of them into the platform meta-table.

# Snapshot Queries

A query that mixes series meta-data and time series data for a given day. Useful
for dumping into tables.

# Table Fetches

It likely makes no sense to query on a series-by-series basis always. Instead, a 
single "table fetch" gets an entire table of series from a provider, and all the series
are updated. The "table fetch" is triggered by an update request on any of the
series in the table.
