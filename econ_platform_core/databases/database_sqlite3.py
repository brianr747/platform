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
import econ_platform_core.databases
import econ_platform_core.utils


class AdvancedDatabase(econ_platform_core.DatabaseManager):
    """
    Abstract base class for all "advanced" databases; similar functionality to SQL databases
    """
    def __init__(self, name='Advanced Database (Abstract)'):
        super().__init__(name=name)
        self.IsAdvanced = True


class DBapiDatabase(AdvancedDatabase):
    """
    Abstract base class for DBAPI2-compliant databases. (Note: not an expert on DBAPI, so this name
    may be shaky.
    """
    def __init__(self, name='DBapi2-compliant SQL Database'):
        super().__init__(name)

class DatabaseSqlite3(DBapiDatabase):
    """
    Class that implements the interface to an SQLite database. This is in the core platform,
    as the sqlite3 library is part of the standard library.

    NOTE: Code will migrate to super-classes. Overall logic into the AdvancedDatabase, SQL high-level logic into
    DBapiDatabase, and low level connection fetching (and SQL syntax) left in here.
    """
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
        self.TableMeta = ''
        self.TableData = ''
        # Allow customisation later...
        self.TableLocal = 'TickerLocal'
        self.TableTickerDataType = 'TickerDataType'
        self.ViewLookup = 'TickerLookup'
        self.TableProviderMeta = 'ProviderMeta'
        self.LogSQL = False

    def GetConnection(self, test_tables=True, auto_create=True):
        if self.Connection is not None:
            return self.Connection
        self.SetParameters()
        full_name = self.DatabaseFile
        if full_name == ':memory:':
            did_not_exist = False
        else:
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
                ('TableMeta', 'meta_table'),
                ('TableData', 'data_table')]
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
            cursor.execute('SELECT * FROM {0} LIMIT 1'.format(self.TableMeta))
        except sqlite3.OperationalError as ex:
            # Expected error message: 'no such table: {table_name}'
            econ_platform_core.log_warning('sqlite3 error %s', ex)
            if self.TableMeta.lower() in ex.args[0].lower():
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
                # No ticker conversion here, but unlikely to appear in an executemany()
                self.Cursor.executemany(cmd, args[0])
            else:
                # Quietly convert tickers to str
                clean_args = []
                for x in args:
                    if issubclass(x.__class__, econ_platform_core.tickers._TickerAbstract):
                        clean_args.append(str(x))
                    else:
                        clean_args.append(x)
                self.Cursor.execute(cmd, clean_args)
        else:
            self.Cursor.execute(cmd)
        if commit_after:
            self.Connection.commit()
        return self.Cursor

    def Exists(self, series_meta):
        self.GetConnection()
        search_query = 'SELECT COUNT(*) FROM {0} WHERE ticker_full = ?'.format(self.TableMeta)
        cursor = self.Execute(search_query, str(series_meta.ticker_full))
        res = cursor.fetchall()
        return res[0][0] > 0

    def Retrieve(self, series_meta):
        self.GetConnection()
        ticker_full = str(series_meta.ticker_full)
        series_id = self.GetSeriesID(ticker_full)
        if series_id is None:
            raise econ_platform_core.TickerNotFoundError('{0} not found on database'.format(ticker_full))
        cmd = """
SELECT series_dates, series_values FROM {0} WHERE series_id = ?
        """.format(self.TableData)
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
        ser.index = pandas.DatetimeIndex(dates)
        ser.name = ticker_full
        return ser


    def Write(self, ser, series_meta, overwrite=True):
        """

        :param ser: pandas.Series
        :param ticker: econ_platform_core.SeriesMetadata
        :param overwrite: bool
        :return:
        """

        series_id = self.GetSeriesID(series_meta.ticker_full)
        if series_id is None:
            self.CreateSeries(series_meta)
            series_id = self.GetSeriesID(series_meta.ticker_full)
        else:
            if not overwrite:
                raise NotImplementedError()
            else:
                # Delete the existing series
                cmd = """
DELETE FROM {0} WHERE series_id = ?""".format(self.TableData)
                self.Execute(cmd, series_id, commit_after=True)
        # Cannot write NULL.
        ser = ser.dropna()
        dates = ser.index
        # Need to coerce to strings.
        dates = [econ_platform_core.utils.coerce_date_to_string(x) for x in dates]
        id_list = [series_id,]*len(dates)
        info = zip(id_list, dates, ser.values)
        cmd = """
        INSERT INTO {0}(series_id, series_dates, series_values) VALUES (?, ?, ?)
        """.format(self.TableData)
        self.Execute(cmd, info, commit_after=True, is_many=True)

    def GetSeriesID(self, full_ticker):
        full_ticker = str(full_ticker)
        self.GetConnection()
        cmd = """
        SELECT series_id FROM {0} WHERE ticker = ? LIMIT 1""".format(self.ViewLookup)
        self.Execute(cmd, full_ticker, commit_after=False)
        res = self.Cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return res[0][0]

    def CreateSeries(self, series_meta):
        """

        :param series_meta: econ_platform_core.SeriesMetadata
        :return:
        """
        # Need to make sure initialised
        self.GetConnection()
        create_str = """
INSERT INTO {0} (series_provider_code, ticker_full, ticker_query, series_name, series_description,
provider_param_string) VALUES
(?, ?, ?, ?, ?, ?)        
        """.format(self.TableMeta)
        local_ticker = series_meta.ticker_local
        if len(local_ticker) == 0:
            local_ticker = None
        self.Execute(create_str, str(series_meta.series_provider_code), str(series_meta.ticker_full),
                     series_meta.ticker_query, series_meta.series_name , series_meta.series_description,
                     econ_platform_core.utils.dict_to_param_string(series_meta.ProviderMetadata),
                     commit_after=True)

    def Delete(self, series_meta, warn_if_non_existent=True):
        """
        Deletes a series; if it does not exist, does nothing.

        :param series_meta: econ_platform_core.SeriesMetadata
        :return: None
        """

        if (series_meta.ticker_full is None) or (len(series_meta.ticker_full) == 0):
            raise NotImplementedError('Must delete by TickerFull specification')
        cmd = """
        DELETE FROM {0} WHERE ticker_full = ?""".format(self.TableMeta)
        self.GetConnection()
        self.Execute(cmd, str(series_meta.ticker_full), commit_after=False)
        if self.Cursor.rowcount > 1:  # pragma: nocover
            # This should never be hit, but it could happen if the SQL command is mangled.
            # Unless cascade deletions are counted...
            raise econ_platform_core.PlatformError(
                'Internal Error! Attempted to delete more than one row!')
        if warn_if_non_existent and 0 == self.Cursor.rowcount:
            econ_platform_core.log_warning('Series to be deleted did not exist: {0}'.format(
                str(series_meta.ticker_full)))
        self.Connection.commit()



    def CreateSqlite3Tables(self):
        """
        Can invoke this by running a script in the scripts directory.
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
        series_name TEXT NULL,
        series_description TEXT NULL,
        series_web_page TEXT NULL,
        table_info TEXT NULL,
        last_update TEXT NULL,
        last_refresh TEXT NULL,
        last_meta_change TEXT NULL,
        discontinued TEXT NULL,
        provider_param_string TEXT NULL
        )
        """.format(self.TableMeta)
        self.Execute(create_1)
        create_2 = """
        CREATE UNIQUE INDEX IF NOT EXISTS index_ticker_full ON {0} (ticker_full)
        """.format(self.TableMeta)
        self.Execute(create_2)
        create_3 = """
        CREATE TABLE IF NOT EXISTS {0} (
        series_id INTEGER,
        series_dates TEXT NOT NULL,
        series_values REAL NOT NULL,
        FOREIGN KEY(series_id) REFERENCES {1}(series_id) ON DELETE CASCADE ON UPDATE CASCADE,
        PRIMARY KEY (series_id, series_dates)
        )""".format(self.TableData, self.TableMeta)
        self.Execute(create_3)
        create_4 = """
CREATE VIEW ViewSummary as 
SELECT m.series_id, m.ticker_full, 
 m.series_provider_code, m.ticker_query, m.series_name, m.series_description, 
 m.series_web_page, m.table_info, m.last_update, m.last_refresh, m.last_meta_change,
 min(d.series_dates) as start_date, max(d.series_dates) as end_date 
 from {0} as m, {1} as d
WHERE m.series_id = d.series_id GROUP BY d.series_id
                 """.format(self.TableMeta, self.TableData)
        self.Execute(create_4)
        self.Connection.commit()
        create_5 = """
        CREATE TABLE IF NOT EXISTS {0} (
        series_id INTEGER,
        ticker_local TEXT,
        FOREIGN KEY(series_id) REFERENCES {1}(series_id) ON DELETE CASCADE ON UPDATE CASCADE,
        PRIMARY KEY (ticker_local)
        )""".format(self.TableLocal, self.TableMeta)
        self.Execute(create_5)
        # create_6 got moved...
        create_7 = """
        CREATE TABLE IF NOT EXISTS {0} (
        series_id INTEGER,
        series_provider_code TEXT,
        param TEXT,
        value TEXT,
        FOREIGN KEY(series_id) REFERENCES {1}(series_id) ON DELETE CASCADE ON UPDATE CASCADE,
        PRIMARY KEY (series_id, param)
        )""".format(self.TableProviderMeta, self.TableMeta)
        self.Execute(create_7)
        create_8 = """
                CREATE TABLE IF NOT EXISTS {0} (
                series_id INTEGER,
                ticker_data_type TEXT,
                security TEXT,
                data_type TEXT,
                FOREIGN KEY(series_id) REFERENCES {1}(series_id) ON DELETE CASCADE ON UPDATE CASCADE,
                PRIMARY KEY (ticker_data_type)
                )""".format(self.TableTickerDataType, self.TableMeta)
        self.Execute(create_8)
        create_9 = """
                CREATE VIEW {0} as 
                SELECT series_id, ticker_full as ticker 
                FROM {1}
                UNION 
                SELECT series_id, ticker_local as ticker FROM {2}
                UNION
                SELECT series_id, ticker_data_type as ticker FROM {3}
                ORDER BY series_id
                                 """.format(self.ViewLookup, self.TableMeta, self.TableLocal,
                                            self.TableTickerDataType)
        self.Execute(create_9)
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

