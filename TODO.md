# TODO List

## Introduction

This file is not in any sense organised. I am just throwing lists of features
that would be useful, without worrying about their priority.

Not including some of the major refactoring things that are part of the design 
document.

# Point Form Items

Stuff that can be summarised easily.
- "Pushed Data provider": data that is pushed to the database; no updates.
- EViews support.
- Bloomberg API.
- Local tickers. (Friendly tickers defined by users.) 
- Data type tickers. For example "IBM|dividend" to get the dividend for "IBM." (The SQLite 
database supports these and local tickers, we just need an API call to insert them. Probably
impemented by the Statscan interface when it is upgraded to handle metadata.)
- Series defined by simple operations: splicing together series, averaging them, etc. The series
may or may not be stored on the database, although I think they may need to be stored on the
database for consistency of treatment with other series (summary view, access by languages
that do not use the Python interface, etc.).
- The *fetch()* command needs to ensure uniformity of dates coming from external
providers. 
- Create config settings to bave default database per provider (e.g., certain commercial providers 
only allow data to go to a particular machine, so that data goes to SQLite).
- Marking series as "discontinued" so that no time is wasted attempting updates.
- Create an "extension manager" class that handles and logs extension loading.
Will be needed if this project grows and new extensions depend on other non-standard
extensions. (Although this is overkill for now, might as well build it before
the back-filling is too complex.)
- Create a "platform doc" function. It can return the doc string (__doc__)
from all the important functions/objects that an external users might touch.
This is not for Python programmers (who can use help(), which does exactly this), rather
for users of external languages or even a local web server. In addition to serving
doc strings, it could give lists of databases, providers, etc.
- Implement "table queries" for Quandl, since the implementation appears borked otherwise.
(Most of the Quandl data seems to be tables...)

**Completed**
- Migrate extensions that use external API's to econ_platform package (out of core).
- Refactor code to use the *tickers.py* module. Eiminate ambiguity about what a ticker
string represents.
- Add "series name"/"series description" as fields that exist for all series. 
Should do quickly, as every provider has to support this!
- Open the provider website based on a platform ticker. Could tie into a local database browser.
- Provider-specific meta-data, specified as key/value pairs. (The SeriesMetadata class has
a class member to hold such data, but needs to be stored to the SQLite database.)
- Allow multiple SQLite database files to be specified by creating new databases in
config settings.
- Providers should be able to open a URL that is specific to a particular series. (For 
providers like FRED or DBnomics, each series has a landing page, for others it will be a table
page, like Statscan.)
- A *fetch_metadata()* command needs to be implemented for "external users."

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

(Completed.)

# Frequency Field

I have so far dodged the issue of data frequency; I have just taken data as-is
from providers, with just some cleaning. (This was what I did for my earlier
personal platform; my R code just cleaned up frequency mismatches as needed.)

However, if we want to step beyond just a descriptive metadata field, frequency
alignment can be complicated. It may be handled at the database level, since
we can imagine two models for such data:

1) All dates are stored as calendar dates (current model). We then need to
ensure that low frequency (weekly -> annual) are saved in a uniform fashion.
2) We save dates in tables based on frequency: daily (and probably weekly) saved
in tables with calendar dates, and lower frequency have either a string
or two columns (e.g., year-month).

I think calendar dates aligned to a common date (e.g., monthly data always
saved to the first of the month) is the best option, but the system should
allow someone to write an extension that uses a different database structure.

# Start Date/End Date

The current code base is greatly simplified because it is dealing with an entire
time series as unit; it just uses whatever time index the external provider or
database uses. However, when we want to update series on databases, or if users
want to specify start date/end date in their *fetch()* calls, we need to 
standardise how date axes are specified. 

I see the need to support at least types of time axes:

1. Calendar date (no time of day parameter).
2. Date-time (if someone has intraday data).
3. Float. Allows us to handle things like model time axes (converting ints to floats
   if needed).
   
One exotic option may be to allow lower frequency dates: monthly, quarterly, etc. 

I am going to dodge this question for as long as possible. For my purposes, I only need
calendar dates and floats (for *sfc_models*). (Since I am using a TEXT field to store the
date information in SQLite, I just have to worry about the date axis formatting at the 
encoding/parsing stage; I can fit all the data into the same column. What we can do is have 
database/provider extensions signal that they can support more advanced time axes as well.
