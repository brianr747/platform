"""
Sqlite3 database. Since the sqlite3 interface is packaged with base Python, a natural starting point.

Get this database running, then will think how to refactor into a generic SQL class. There are some packages that
handle wrapping, but may be overkill for my purposes.

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

import os
import pandas
import sqlite3
import datetime

import econ_platform_core
import econ_platform_core.utils

class DatabaseSqlite3(econ_platform_core.DatabaseManager):
    Cursor: sqlite3.Cursor
    Directory: str
    Connection: sqlite3.Connection

    def __init__(self):
        """
        Initialise the object. Note: Does nothing, including looking up configuration information.

        """
        super().__init__(name='SQLite Database')
        self.Name = 'SQLite Database'
        self.DatabaseFile = ''
        self.Connection = None
        self.Cursor = None
        self.MetaTable = ''
        self.DataTable = ''
        self.LogSQL = False

    def GetConnection(self, test_tables=True, auto_create=True):
        if self.Connection is not None:
            return self.Connection
        self.SetParameters()
        full_name = self.DatabaseFile
        did_not_exist = not os.path.exists(full_name)
        self.Connection = sqlite3.Connection(full_name)
        if did_not_exist and auto_create:
            create_sqlite3_tables()
            return self.Connection
        # Test to see whether the tables exist!
        if test_tables:
            self.TestTablesExist()
        return self.Connection

    def SetParameters(self):
        # Set data from config file, unless previously set
        # List of (class_member, config_attribute) pairs.
        info = [('DatabaseFile', 'file_name'),
                ('MetaTable', 'meta_table'),
                ('DataTable', 'data_table')]
        for attrib, config_name in info:
            # If len() > 0, then already set
            if len(getattr(self, attrib)) == 0:
                # Can either be under "SQL" or "D_SQLITE3"
                try:
                    setattr(self, attrib, econ_platform_core.PlatformConfiguration['SQL'][config_name])
                except KeyError:
                    setattr(self, attrib, econ_platform_core.PlatformConfiguration['D_SQLITE'][config_name])
        # Database file is a special case.
        self.DatabaseFile = econ_platform_core.utils.parse_config_path(self.DatabaseFile)



    def TestTablesExist(self):
        cursor = self.Connection.cursor()
        # If the meta table is there, so it the values table?
        # Don't know how to validate existence of SQL objects, so do it this way
        try:
            cursor.execute('SELECT * FROM {0} LIMIT 1'.format(self.MetaTable))
        except sqlite3.OperationalError as ex:
            # Expected error message: 'no such table: {table_name}'
            econ_platform_core.log_warning('sqlite3 error %s', ex)
            if self.MetaTable.lower() in ex.args[0].lower():
                raise econ_platform_core.PlatformError('Tables do not exist. Need to run the initialisation script init_sqlite.py in the scripts directory.')
            else:
                print(str(ex))
                raise econ_platform_core.PlatformError('Error when testing for table existence')

    def Execute(self, cmd, *args, commit_after=False, is_many=False):
        """
        Convenience function that logs commands if self.LogSQL is True.

        :param cmd: str
        :param args:
        :param commit_after: bool
        :return: sqlite3.Cursor
        """
        if self.Connection is None:
            self.GetConnection(test_tables=False)
        if self.Cursor is None:
            self.Cursor = self.Connection.cursor()
        if self.LogSQL:
            if len(args) > 0:
                if is_many:
                    econ_platform_core.log('{0} : executemany()'.format(cmd))
                else:
                    econ_platform_core.log(cmd + " : " + str(args))
            else:
                econ_platform_core.log(cmd)
        if len(args) > 0:
            if is_many:
                self.Cursor.executemany(cmd, args[0])
            else:
                self.Cursor.execute(cmd, args)
        else:
            self.Cursor.execute(cmd)
        if commit_after:
            self.Connection.commit()
        return self.Cursor

    def Exists(self, full_ticker):
        self.GetConnection()
        search_query = 'SELECT COUNT(*) FROM {0} WHERE ticker_full = ?'.format(self.MetaTable)
        cursor = self.Execute(search_query, full_ticker)
        res = cursor.fetchall()
        return res[0][0] > 0

    def Retrieve(self, series_meta):
        self.GetConnection()
        try:
            ticker_full = series_meta.ticker_full
        except:
            ticker_full = series_meta
        series_id = self.GetSeriesID(ticker_full)
        if series_id is None:
            raise econ_platform_core.TickerNotFoundError('{0} not found on database'.format(ticker_full))
        cmd = """
SELECT series_dates, series_values FROM {0} WHERE series_id = ?
        """.format(self.DataTable)
        res = self.Execute(cmd, series_id, commit_after=False).fetchall()
        def mapper(s):
            try:
                return econ_platform_core.utils.iso_string_to_date(s)
            except:
                float(s)
        try:
            dates = [mapper(x[0]) for x in res]
        except:
            raise econ_platform_core.PlatformError('Corrupted date axis for {0}'.format(ticker_full))
        valz = [x[1] for x in res]
        ser = pandas.Series(valz)
        ser.index = dates
        ser.name = ticker_full
        return ser


    def Write(self, ser, series_meta, overwrite=True):
        """

        :param ser: pandas.Series
        :param ticker: econ_platform_core.SeriesMetaData
        :param overwrite: bool
        :return:
        """

        series_id = self.GetSeriesID(series_meta.ticker_full)
        if series_id is None:
            self.CreateSeries(series_meta)
        else:
            if not overwrite:
                raise NotImplementedError()
            else:
                # Delete the existing series
                cmd = """
DELETE FROM {0} WHERE series_id = ?""".format(self.DataTable)
                self.Execute(cmd, series_id, commit_after=True)
        dates = ser.index
        # Need to coerce to strings.
        dates = [econ_platform_core.utils.coerce_date_to_string(x) for x in dates]
        id_list = [series_id,]*len(dates)
        info = zip(id_list, dates, ser.values)
        cmd = """
        INSERT INTO {0}(series_id, series_dates, series_values) VALUES (?, ?, ?)
        """.format(self.DataTable)
        self.Execute(cmd, info, commit_after=True, is_many=True)

    def GetSeriesID(self, full_ticker):
        self.GetConnection()
        cmd = """
        SELECT series_id FROM {0} WHERE ticker_full = ?""".format(self.MetaTable)
        self.Execute(cmd, full_ticker, commit_after=False)
        res = self.Cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return res[0][0]

    def CreateSeries(self, series_meta):
        """

        :param series_meta: econ_platform_core.SeriesMetaData
        :return:
        """
        # Need to make sure initialised
        self.GetConnection()
        create_str = """
INSERT INTO {0} (series_provider_code, ticker_full, ticker_local, ticker_query) VALUES
(?, ?, ?, ?)        
        """.format(self.MetaTable)
        local_ticker = series_meta.ticker_local
        if len(local_ticker) == 0:
            local_ticker = None
        self.Execute(create_str, series_meta.series_provider_code, series_meta.ticker_full,
                     local_ticker, series_meta.ticker_query, commit_after=True)


    def CreateSqlite3Tables(self):
        """
        Can invoke this by running the
        :return:

        """
        self.LogSQL = True
        # Need to call this to initialise parameters...
        self.GetConnection(test_tables=False)
        # Don't test the table existence for duh reasons
        # Can't use the "?" query parameters for table names
        create_1 = """
        CREATE TABLE IF NOT EXISTS {0} (
        series_id INTEGER PRIMARY KEY, 
        ticker_full TEXT NOT NULL, 
        series_provider_code TEXT NOT NULL, 
        ticker_query TEXT NOT NULL,
        ticker_local TEXT
        )
        """.format(self.MetaTable)
        self.Execute(create_1)
        create_2 = """
        CREATE UNIQUE INDEX IF NOT EXISTS index_ticker_full ON {0} (ticker_full)
        """.format(self.MetaTable)
        self.Execute(create_2)
        create_3 = """
        CREATE TABLE IF NOT EXISTS {0} (
        series_id INTEGER,
        series_dates TEXT NOT NULL,
        series_values REAL NOT NULL,
        FOREIGN KEY(series_id) REFERENCES {1}(series_id) ON DELETE CASCADE ON UPDATE CASCADE,
        PRIMARY KEY (series_id, series_dates)
        )""".format(self.DataTable, self.MetaTable)
        self.Execute(create_3)
        create_4 = """
CREATE VIEW SummaryView as 
SELECT m.series_id, m.ticker_full, 
 m.series_provider_code, m.ticker_query, m.ticker_local,
 min(d.series_dates) as start_date, max(d.series_dates) as end_date 
 from {0} as m, {1} as d
WHERE m.series_id = d.series_id
                 """.format(self.MetaTable, self.DataTable)
        self.Execute(create_4)
        self.Connection.commit()
        self.TestTablesExist()
        self.Connection.commit()

def create_sqlite3_tables():
    """
    Create the tables if they are not in the database file.

    Can be invoked by running the script init_sqlite.py in the scripts directory.

    :return:
    """
    obj = DatabaseSqlite3()
    obj.CreateSqlite3Tables()
    # Close the connection...
    del obj
    # Do test.
    obj2 = DatabaseSqlite3()
    obj2.GetConnection(test_tables=True)

