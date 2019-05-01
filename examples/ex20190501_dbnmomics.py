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
    import dbnomics
except ImportError:
    print('Need to install dbnomics -  pip install dbnomics')
    raise


def describe(x):
    print('Object Description:')
    print('Type is:', type(x))
    try:
        print(x.head())
    except:
        print(x)


print('Fetch a single series: Greek nominal GDP.')

df1 = dbnomics.fetch_series('Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL')
describe(df1)
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



