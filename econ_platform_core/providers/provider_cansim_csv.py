"""
provider_cansim_csv.py

Handles CANSIM (or whatever StatsCan calls their database now) CSV files.

TODO: allow incremental updates on a per-ticker basis, using their API. May need to rename this provider.

Not sure whether it is better to use SDMX or stick with CSV's for initial data stocking.

Since this module has no dependencies on anything outside econ_platform_core or standard libraries, can stay in the
core.

Note: Certain tables from the Bank of Canada inexplicably contain 0 instead of NaN. I am eating those entries,
but I hope that the BoC will get their act together...

Assumes English webpages and file names.

The workflow of this provider is now quite unusual. I save the list of vectors to a manifest file once the table is
processed. If this manifest file exists, it is checked for the given vector: if it is not there, a TickerNotFound
error is thrown. Otherwise, the full file would be scanned looking for the non-existent ticker.

Once the update protocol is more advanced, this will be probably be rebuilt.

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
import glob

import econ_platform_core
import econ_platform_core.entity_and_errors
import econ_platform_core.series_metadata
from econ_platform_core import log, log_warning
import econ_platform_core.configuration
import econ_platform_core.utils
import econ_platform_core.tickers as tickers


class ProviderCansim_Csv(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderCansim_Csv, self).__init__(name='CANSIM_CSV')
        self.DataDirectory = econ_platform_core.utils.parse_config_path(
            econ_platform_core.PlatformConfiguration['P_STATSCAN']['directory'])
        self.ZipTail = econ_platform_core.PlatformConfiguration['P_STATSCAN']['zip_tail']
        # If anyone from the Bank of Canada sees this and is offended, get these table(s) fixed!
        self.BorkedBankOfCanadaTables = ['10100139',]
        self.WebPage = 'https://www150.statcan.gc.ca/n1/en/type/data?MM=1'
        self.MetaMapper = {}


    def GetTableUrl(self, table):
        """
        Get the URL for a table; no series-specific URL's (yet).
        :param table: str
        :return: str
        """
        return 'https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={0}'.format(table)

    def _GetSeriesUrlImplementation(self, series_meta):
        """
        Get the webpage for the table associated with a series.

        :param series_meta: econ_platform_core.SeriesMetadata
        :return: str
        """
        ticker_query = str(series_meta.ticker_query)
        try:
            table_name, vector = ticker_query.split('|')
        except:
            raise econ_platform_core.entity_and_errors.TickerError('CANSIM_CSV ticker format: <table>|<vector>; invalid ticker = {0}'.format(
                                         ticker_query)) from None
        return self.GetTableUrl(table_name)



    def fetch(self, series_meta):
        """
        Do the fetch from CSV.

        Increments may be via JSON.

        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        query_ticker = str(series_meta.ticker_query)
        try:
            table_name, vector = query_ticker.split('|')
        except:
            raise econ_platform_core.entity_and_errors.TickerError('CANSIM_CSV ticker format: <table>|<vector>; invalid ticker = {0}'.format(
                                         query_ticker))
        target = os.path.join(self.DataDirectory, '{0}.csv'.format(table_name))
        if not os.path.exists(target):
            econ_platform_core.log('Table file does not exist, attempting to unzip')
            try:
                self.UnzipFile(table_name)
            except:
                raise econ_platform_core.entity_and_errors.PlatformError(
                    'Table {0} needs to be downloaded as a zip file into {1}'.format(table_name, self.DataDirectory)) from None
        # Do the whole table
        self.TableWasFetched = True
        self.TableMeta = {}
        self.TableSeries = {}
        self.MetaMapper = {}
        self.ParseUnzipped(table_name)
        self.BuildSeries()
        self.ArchiveFiles(table_name)
        try:
            ser = self.TableSeries[str(series_meta.ticker_full)]
            meta = self.TableMeta[str(series_meta.ticker_full)]
        except KeyError:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('{0} was not found'.format(str(series_meta.ticker_full))) \
                from None
        return ser, meta

    def UnzipFile(self, table_name):
        fname = table_name + self.ZipTail
        full_name = os.path.join(self.DataDirectory, fname)
        log('Unzipping %s', full_name)
        with zipfile.ZipFile(full_name, 'r') as myzip:
            info = myzip.infolist()
            expected_names = [table_name + '.csv', table_name + '_MetaData.csv']
            for i in info:
                if i.filename in expected_names:
                    log('Extracting file %s', i.filename)
                else:
                    log_warning('Unexpected file name: %s', i.filename)
                myzip.extract(i, self.DataDirectory)

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
        target = os.path.join(self.DataDirectory, '{0}.csv'.format(table_name))
        # 2 output files (for now)
        # Save the last row for each vector
        target_col_names = ['vector', 'ref_date', 'value']
        last_rows = {}
        is_borked_file = table_name in self.BorkedBankOfCanadaTables
        parsed_name = os.path.join(self.DataDirectory, '{0}_parsed.txt'.format(table_name))
        with open(parsed_name, 'w') as f_series:
            out_header = ['vector', econ_platform_core.PlatformConfiguration['Database']['dates_column'],
                          econ_platform_core.PlatformConfiguration['Database']['values_column']]
            f_series.write('\t'.join(out_header) +'\n')
            with open(os.path.join(self.DataDirectory, '{0}_snapshot.txt'.format(table_name)), 'w') as f_meta:
                with open(target, 'r') as csvfile:
                    reader = csv.reader(csvfile, quotechar='"')
                    # How's that for nesting, eh?
                    header = next(reader)
                    header = [x.replace('"', '') for x in header]
                    # There is an encoding marker in the first row; nuke it from orbit.
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
                            value = float(data_row[-1])
                            # If we are in a borked file, eat any 0 values.
                            # This operation is dangerous; I sent an e-mail to Statscan asking them to
                            # ask the BoC to get their act together...
                            if is_borked_file and 0. == value:
                                continue
                        except ValueError:
                            continue
                        # Only save the row in the summary if it has data.
                        last_rows[vector] = tuple(row)
                        # Convert the date
                        data_row[1] = self.ParseDate(data_row[1]).isoformat()
                        f_series.write('\t'.join(data_row) + '\n')
                        if vector in self.TableSeries:
                            self.TableSeries[vector].append((data_row[1], value))
                        else:
                            self.TableSeries[vector] = [(data_row[1], value)]
                            self.TableMeta[vector] = self.CreateMetadata(table_name, row, header)
                vector_list = list(last_rows.keys())
                vector_list.sort()
                for v in vector_list:
                    value = last_rows[v]
                    if len(value[vector_col]) == 0:
                        raise ValueError('Huh')
                    f_meta.write('\t'.join(value) + '\n')

    def CreateMetadata(self, table_name, row, header):
        if len(self.MetaMapper) == 0:
            ignore_list = ('REF_DATE', 'VALUE')
            keep_list = []
            for i in range(0, len(header)):
                if header[i] not in ignore_list:
                    keep_list.append(i)
            keep_list = tuple(keep_list)
            try:
                uom_pos = econ_platform_core.utils.entry_lookup('UOM', header)
                desc_list = []
                ignore_2 = ('REF_DATE', 'DGUID')
                for i in range(0, uom_pos):
                    if header[i] not in ignore_2:
                        desc_list.append(i)
                desc_list = tuple(desc_list)
            except KeyError:
                desc_list = ()
            self.MetaMapper['keep_list'] = keep_list
            self.MetaMapper['desc_list'] = desc_list
        else:
            keep_list = self.MetaMapper['keep_list']
            desc_list = self.MetaMapper['desc_list']
        meta = econ_platform_core.series_metadata.SeriesMetadata()
        for i in keep_list:
            meta.ProviderMetadata[header[i]] = row[i]
        vector = meta.ProviderMetadata['VECTOR']
        query_ticker = '{0}|{1}'.format(table_name, meta.ProviderMetadata['VECTOR'])
        meta.ticker_query = tickers.TickerFetch(query_ticker)
        meta.series_provider_code = tickers.TickerProviderCode(self.ProviderCode)
        meta.ticker_full = tickers.create_ticker_full(meta.series_provider_code, meta.ticker_query)
        if len(desc_list) == 0:
            meta.series_name = 'Statscan series with VECTOR={0}. Unable to create name.'.format(vector)
            meta.series_description = 'Statscan series VECTOR={0}, From Table={1}. Unable to create name.'.format(
                vector, table_name)
        else:
            ser_info = []
            for idx in desc_list:
                ser_info.append(row[idx])
            sername = '; '.join(ser_info)
            meta.series_name = sername
            meta.series_description = '{0} From StatsCan Table {1}, Vector = {2}'.format(sername, table_name,
                                                                                         vector)
        return meta

    def BuildSeries(self):
        """
        Build the series from data collected from file.


        :return:
        """
        # Need to remap to use the full ticker.
        new_series = {}
        new_meta = {}
        for vector in self.TableSeries.keys():
            ser_data = self.TableSeries[vector]
            meta = self.TableMeta[vector]
            ser_data.sort()
            ddates = [x[0] for x in ser_data]
            values = [x[1] for x in ser_data]
            ser = pandas.Series(values)
            ser.index = ddates
            ticker_full = str(meta.ticker_full)
            ser.name = ticker_full
            new_series[ticker_full] = ser
            new_meta[ticker_full] = meta
        self.TableMeta = new_meta
        self.TableSeries = new_series

    def ArchiveFiles(self, table_name):
        """
        Move all the files associated with a table to the archive subdirectory.

        :param table_name: str
        :return:
        """
        flist = glob.glob(os.path.join(self.DataDirectory, table_name + '*'))
        for fname in flist:
            econ_platform_core.utils.archive_file(os.path.join(self.DataDirectory, fname))




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