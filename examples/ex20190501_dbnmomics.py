"""
ex2019050_dbnomics.py

Just some initial examples for DBnomics queries. Using the raw interface calls, as well as using myplatform functions.

Uses Python 3.7. Obviously need to install the dbnomics package. The "myplatform" package will need to be
installed for the later parts of the code to work.

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


# Just execute the code as a script.
print('Starting example')
try:
    import pandas
    import dbnomics
except ImportError:
    print('Need to install pandas and dbnomics -  pip install dbnomics')
    raise



print("""Fetch a single series: Greek nominal GDP.
Got the code from the series webpage.
Code: 'Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL'
URL: https://db.nomics.world/Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL
""")

df1 = dbnomics.fetch_series('Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL')
print('Object returned by fetch_series:')
print('Type:', type(df1))
print('Some of the data')
print(df1.head())
input('Hit Return to continue')
print('Columns of the dataframe:')
print(df1.columns)

print('This is a lot of columns. Useful, but often extraneous for analysis.')
print('The values of the time series:')
print(df1['value'])
print('This is indexed by the dataframe row number. We also need the time axis [period]')
print(df1['period'])
input('Hit any key; attempting to plot')

try:
    import matplotlib.pyplot
    # If we skip the next two lines, the plot throws up a warning...
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
    # Plot
    matplotlib.pyplot.plot(df1['period'], df1['value'])
except:
    print('Plot failed. Need matplotlib to be installed. Skipping...')

input('Hit return to continue')

print("""
DBnomics also supports more advanced query options. I will just grab two series for simplicity.
The Greek GDP series (again), and some other series from their example code...

At present, the dbnomics code throws up a pandas warning for me...
""")

df2 = dbnomics.fetch_series(['AMECO/ZUTN/EA19.1.0.0.0.ZUTN', 'Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL'])

print('The two time series live in a single pandas DataFrame')

print(df2.head(100))
print("""We want to unpack these into separate time series objects. We use the loc() method to do this""")

df_ser1 = df2.loc[df2['series_code'] == 'Q.CP_MEUR.SCA.B1GQ.EL']
df_ser2 = df2.loc[df2['series_code'] == 'EA19.1.0.0.0.ZUTN']
print('First series')
print(df_ser1.head())
print('Second Series')
print(df_ser2.head())
input('Hit return to continue')
print("""
These "series" are still data frames. To be more convenient, need to convert to pandas Series.""")

ser1 = pandas.Series(df_ser1.value)
ser1.index = df_ser1.period

ser2 = pandas.Series(df_ser2.value)
ser2.index = df_ser2.period
print('Second series has "NA": convert to NaN')
import numpy
print(ser2)
ser2 = ser2.replace('NA', numpy.nan)
print(ser2)
print('Get rid of NaN')
ser2 = ser2.dropna()
print(ser2)





