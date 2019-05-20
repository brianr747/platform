"""
provider_cansim_csv.py

Handles CANSIM (or whatever StatsCan calls their database now) CSV files.

Will switch over to SDMX (maybe), but the text files are easy to work with...

Since this module has no dependencies on anything outside econ_platform_core or standard libraries, can stay in the
core.

Note: Certain tables from the Bank of Canada inexplicably contain 0 instead of NaN. I am eating those entries,
but I hope that the BoC will get their act together...

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

import zipfile
import csv
import os
import pandas

import econ_platform_core
from econ_platform_core import log, log_warning
import econ_platform_core.configuration
import econ_platform_core.utils


class ProviderCansim_Csv(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderCansim_Csv, self).__init__(name='CANSIM_CSV')
        self.DirectoryZip = econ_platform_core.utils.parse_config_path(
            econ_platform_core.PlatformConfiguration['P_CCSV']['zip_directory'])

        self.DirectoryParsed = econ_platform_core.utils.parse_config_path(
            econ_platform_core.PlatformConfiguration['P_CCSV']['parsed_directory'])
        self.ZipTail = econ_platform_core.PlatformConfiguration['P_CCSV']['zip_tail']
        # If anyone from the Bank of Canada sees this and is offended, get these table(s) fixed!
        self.BorkedBankOfCanadaTables = ['10100139']


    def fetch(self, series_meta):
        """
        Do the fetch.

        Can only support single series queries...
        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        query_ticker = str(series_meta.ticker_query)
        try:
            table_name, vector = query_ticker.split('|')
        except:
            raise econ_platform_core.TickerError('CANSIM_CSV ticker format: <table>|<vector>; invalid ticker = {0}'.format(
                                         query_ticker))
        parsed_name = self.GetTimeSeriesFile(table_name)
        if not os.path.exists(parsed_name):
            econ_platform_core.log('Table file does not exist, attempting to unzip')
            try:
                self.UnzipFile(table_name)
            except:
                raise econ_platform_core.TickerNotFoundError(
                    'Table {0} needs to be downloaded as a zip file'.format(table_name))
            self.ParseUnzipped(table_name)
        items = []
        with open(parsed_name, 'r') as f:
            for row_raw in f:
                row = row_raw.split('\t')
                if row[0] == vector:
                    ddate = econ_platform_core.utils.iso_string_to_date(row[1])
                    items.append((ddate, float(row[2])))
        if len(items) == 0:
            raise econ_platform_core.TickerNotFoundError('Vector {0} not found in CANSIM table {1}'.format(vector, table_name))
        items.sort()
        values = [x[1] for x in items]
        dates = [x[0] for x in items]
        data = pandas.Series(values)
        data.index = dates
        data.name = '{0}@{1}'.format(self.ProviderCode, query_ticker)
        return data

    def GetTimeSeriesFile(self, table_name):
        return os.path.join(self.DirectoryParsed, 'parsed_{0}.txt'.format(table_name))

    def UnzipFile(self, table_name):
        fname = table_name + self.ZipTail
        full_name = os.path.join(self.DirectoryZip, fname)
        log('Unzipping %s', full_name)
        with zipfile.ZipFile(full_name, 'r') as myzip:
            info = myzip.infolist()
            expected_names = [table_name + '.csv', table_name + '_MetaData.csv']
            for i in info:
                if i.filename in expected_names:
                    log('Extracting file %s', i.filename)
                else:
                    log_warning('Unexpected file name: %s', i.filename)
                myzip.extract(i, self.DirectoryParsed)

    def ParseDate(self, date_str):
        if len(date_str) == 7:
            # Monthly?
            ddate = econ_platform_core.utils.align_by_month(date_str[0:4], date_str[-2:], freq='M')
        elif len(date_str) == 10:
            ddate = econ_platform_core.utils.iso_string_to_date(date_str)
        else:
            raise NotImplementedError('Unknown CANSIM date format: {0}'.format(date_str))
        return ddate

    def ParseUnzipped(self, table_name):
        """
        Note: use ".txt" instead of CSV since Excel cannot import the files properly. (Great job, Redmond!)

        :param table_name:
        :return:
        """
        target = os.path.join(self.DirectoryParsed, '{0}.csv'.format(table_name))
        # 2 output files (for now)
        # Save the last row for each vector
        target_col_names = ['vector', 'ref_date', 'value']
        last_rows = {}
        is_borked_file = table_name in self.BorkedBankOfCanadaTables
        with open(self.GetTimeSeriesFile(table_name), 'w') as f_series:
            out_header = ['vector', econ_platform_core.PlatformConfiguration['Database']['dates_column'],
                          econ_platform_core.PlatformConfiguration['Database']['values_column']]
            f_series.write('\t'.join(out_header) +'\n')
            with open(os.path.join(self.DirectoryParsed, 'snapshot_{0}.txt'.format(table_name)), 'w') as f_meta:
                with open(target, 'r') as csvfile:
                    reader = csv.reader(csvfile, quotechar='"')
                    # How's that for nesting, eh?
                    header = next(reader)
                    header = [x.replace('"', '') for x in header]
                    # There seems to be some garbage in the first entry; nuke it from orbit.
                    header = [econ_platform_core.utils.remove_non_ascii(x) for x in header]
                    f_meta.write(('\t'.join(header)) + '\n')
                    # Find the columns
                    try:
                        targ_col_n = [econ_platform_core.utils.entry_lookup(x, header, case_sensitive=False)
                                      for x in target_col_names]
                    except KeyError:
                        print('CANSIM CSV format changed!')
                        raise
                    vector_col = targ_col_n[0]
                    for row in reader:
                        vector = row[vector_col]
                        data_row = [row[x] for x in targ_col_n]
                        try:
                            # If we cannot convert to float, do not write.
                            x = float(data_row[-1])
                            # If we are in a borked file, eat any 0 values.
                            # This operation is dangerous; I sent an e-mail to Statscan asking them to
                            # ask the BoC to get their act together...
                            if is_borked_file and 0. == x:
                                continue
                            # Only save the row in the summary if it has data.
                            last_rows[vector] = tuple(row)
                            # Convert the date
                            data_row[1] = self.ParseDate(data_row[1]).isoformat()
                            f_series.write('\t'.join(data_row) + '\n')
                        except ValueError:
                            pass
                vector_list = list(last_rows.keys())
                vector_list.sort()
                for v in vector_list:
                    x = last_rows[v]
                    if len(x[vector_col]) == 0:
                        raise ValueError('Huh')
                    f_meta.write('\t'.join(x) + '\n')



def main():
    """
    Routine used in testing. Not really a good candidate for test-driven development...
    :return:
    """
    econ_platform_core.configuration.print_configuration()
    econ_platform_core.start_log()
    obj = ProviderCansim_Csv()
    # obj.ParseUnzipped('10100002')
    ser = econ_platform_core.fetch('CCSV@10100002|v86822808')
    # econ_platform.analysis.quick_plot.quick_plot(ser)


if __name__ == '__main__':
    main()