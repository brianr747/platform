"""
provider_cansim_csv.py

Handles CANSIM (or whatever StatsCan calls their database now) CSV files.

Will switch over to SDMX (maybe), but the text files are easy to work with...

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

import myplatform
from myplatform import log, log_warning
import myplatform.configuration
import myplatform.utils


class ProviderCansim_Csv(myplatform.ProviderWrapper):
    def __init__(self):
        super(ProviderCansim_Csv, self).__init__(name='CANSIM_CSV')
        self.DirectoryZip = myplatform.PlatformConfiguration['P_CCSV']['zip_directory']
        if self.DirectoryZip == 'cansim_csv':
            # Put it into the sub-directory
            self.DirectoryZip = os.path.join(os.path.dirname(__file__), 'cansim_csv')
        self.DirectoryParsed = myplatform.PlatformConfiguration['P_CCSV']['parsed_directory']
        if self.DirectoryParsed == 'cansim_csv/parsed':
            self.DirectoryParsed = os.path.join(os.path.dirname(__file__), 'cansim_csv', 'parsed')
        self.ZipTail = myplatform.PlatformConfiguration['P_CCSV']['zip_tail']


    def fetch(self, series_meta):
        """
        Do the fetch.

        Can only support single series queries...
        :param series_meta: myplatform.SeriesMetaData
        :return: list
        """
        query_ticker = series_meta.ticker_query
        try:
            table_name, vector = query_ticker.split('|')
        except:
            raise myplatform.TickerError('CANSIM_CSV ticker format: <table>|<vector>; invalid ticker = {0}'.format(
                                         query_ticker))
        parsed_name = self.GetTimeSeriesFile(table_name)
        if not os.path.exists(parsed_name):
            myplatform.log('Table file does not exist, attempting to unzip')
            try:
                self.UnzipFile(table_name)
            except:
                raise myplatform.TickerNotFoundError(
                    'Table {0} needs to be downloaded as a zip file'.format(table_name))
            self.ParseUnzipped(table_name)
        items = []
        with open(parsed_name, 'r') as f:
            for row_raw in f:
                row = row_raw.split('\t')
                if row[0] == vector:
                    ddate = myplatform.utils.iso_string_to_date(row[1])
                    items.append((ddate, float(row[2])))
        if len(items) == 0:
            raise myplatform.TickerNotFoundError('Vector {0} not found in CANSIM table {1}'.format(vector, table_name))
        items.sort()
        values = [x[1] for x in items]
        dates = [x[0] for x in items]
        data = pandas.Series(values)
        data.index = dates
        data.name = '{0}@{1}'.format(self.ProviderCode, query_ticker)
        return [data,]

    def GetTimeSeriesFile(self, table_name):
        return os.path.join(self.DirectoryParsed, 'parsed_{0}.csv'.format(table_name))

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
            ddate = myplatform.utils.align_by_month(date_str[0:4], date_str[-2:], freq='M')
        else:
            raise NotImplementedError('Unknown CANSIM date format: {0}'.format(date_str))
        return ddate

    def ParseUnzipped(self, table_name):
        target = os.path.join(self.DirectoryParsed, '{0}.csv'.format(table_name))
        # 2 output files (for now)
        # Save the last row for each vector
        target_col_names = ['vector', 'ref_date', 'value']
        last_rows = {}
        with open(self.GetTimeSeriesFile(table_name), 'w') as f_series:
            out_header = ['vector', myplatform.PlatformConfiguration['Database']['dates_column'],
                      myplatform.PlatformConfiguration['Database']['values_column']]
            f_series.write('\t'.join(out_header) +'\n')
            with open(os.path.join(self.DirectoryParsed, 'snapshot_{0}.csv'.format(table_name)), 'w') as f_meta:
                with open(target, 'r') as csvfile:
                    reader = csv.reader(csvfile, quotechar='"')
                    # How's that for nesting, eh?
                    header = next(reader)
                    header = [x.replace('"', '') for x in header]
                    # There seems to be some garbage in the first entry; nuke it from orbit.
                    header = [myplatform.utils.remove_non_ascii(x) for x in header]
                    f_meta.write('\t'.join(header))
                    # Find the columns
                    try:
                        targ_col_n = [myplatform.utils.entry_lookup(x, header, case_sensitive=False)
                                     for x in target_col_names]
                    except KeyError:
                        print('CANSIM CSV format changed!')
                        raise
                    vector_col = targ_col_n[0]
                    for row in reader:
                        vector = row[vector_col]
                        last_rows[vector] = row
                        data_row = [row[x] for x in targ_col_n]
                        try:
                            # If we cannot convert to float, do not write.
                            float(data_row[-1])
                            # Convert the date
                            data_row[1] = self.ParseDate(data_row[1]).isoformat()
                            f_series.write('\t'.join(data_row) + '\n')
                        except ValueError:
                            pass
                vector_list = list(last_rows.keys())
                vector_list.sort()
                for v in vector_list:
                    f_meta.write('\t'.join(last_rows[v]) + '\n')



def main():
    """
    Routine used in testing. Not really a good candidate for test-driven development...
    :return:
    """
    myplatform.configuration.print_configuration()
    myplatform.start_log()
    obj = ProviderCansim_Csv()
    # obj.ParseUnzipped('10100002')
    ser = myplatform.fetch('CCSV@10100002|v86822808')
    myplatform.quick_plot(ser)


if __name__ == '__main__':
    main()