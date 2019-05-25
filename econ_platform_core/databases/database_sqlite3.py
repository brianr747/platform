"""
Sqlite3 database. Since the sqlite3 interface is packaged with base Python,
a natural starting point.

This database has a special feature: it is designed to add extra databases solely
by modifying the config fig.

In the config_default, we see:

[D_SQLITE_EXTRA]
TMP={DATA}\platform_tmp.db

This means that there is an extra database (with code "TMP" saved in the file "platform_tmp.db"
in the econ_platform_core/data directory.

You can add more database files under new codes by adding an [D_SQLITE_EXTRA] entry
in your site/user config files, e.g.:

[D_SQLITE_EXTRA]
SCRATCH=<path>scratch.db

This means that you can fetch({ticker}, 'SCRATCH') and use that database. This is useful for
development, as you can write to these side databases (and delete them) as you experiment
with new data sources, without affecting your main database.

(Other SQL databases could emulate this, but not very easily in the cases where analysts do not
have permissions to create tables. Working with local database files is probably the cleanest
way to create a distinction between "production" and "development" environments: once the new
code is ready for prime time, you just point it at the production server instead of a local file.)

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
import econ_platform_core.entity_and_errors
import econ_platform_core.series_metadata
import econ_platform_core.utils
from econ_platform_core.databases import AdvancedDatabase


class DBapiDatabase(AdvancedDatabase):
    """
    Abstract base class for DBAPI2-compliant databases. (Note: not an expert on DBAPI, so this name
    may be shaky.)

    My focus is on the SQLAlchemy-based classes; this class will be for anyone who wants to stick with an interface

    that is staright SQL.
    """
    def __init__(self, name='DBapi2-compliant SQL Database'):
        super().__init__(name)

class DatabaseSqlite3(DBapiDatabase):
    """
    Class that implements the interface to an SQLite database. This is in the core platform,
    as the sqlite3 library is part of the standard library.

    This class uses the dbapi interface, which is perhaps more familiar to more people. However, my development
    efforts are probably going towards the SQLalchemy-based classes, and this class will not have the full feature
    set of the SQLalchemy ones.

    By adding entries into the config file section 'D_SQLITE_EXTRA', you can create extra SQLite databases with
    different filenames/codes. (Useful for testing, or to segregate data.) By default, there is a "TMP" database
    created.

    NOTE: Code will migrate to super-classes. Overall logic into the AdvancedDatabase, SQL high-level logic into
    DBapiDatabase, and low level connection fetching (and SQL syntax) left in here. I am refactoring the base classes
    first, and then will fix this class last. (I added public methods to this class, but the design is now that these
    derived classes should only override the non-public implementation methods.)

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
        self.AutoCreate = True


    def _Connect(self):
        """
        Implementation of database connection.
        :return:
        """
        if self.Connection is not None:
            return self.Connection
        self.SetParameters()
        full_name = self.DatabaseFile
        if full_name == ':memory:':
            did_not_exist = True
        else:
            did_not_exist = not os.path.exists(full_name)
        if did_not_exist and self.AutoCreate:
            self.CreateSqlite3Tables()
            return self.Connection
        self.Connection = sqlite3.Connection(full_name)
        self.HandleDatabase = self.Connection

    def SetParameters(self):
        # Set data from config file, unless previously set
        if len(self.DatabaseFile) == 0:
            self.DatabaseFile = econ_platform_core.PlatformConfiguration['D_SQLITE']['file_name']
        if len(self.TableMeta) == 0:
            self.TableMeta = econ_platform_core.PlatformConfiguration['SQL']['meta_table']
        if len(self.TableData) == 0:
            self.TableData = econ_platform_core.PlatformConfiguration['SQL']['data_table']

        # Database file is a special case.
        self.DatabaseFile = econ_platform_core.utils.parse_config_path(self.DatabaseFile)


    def TestTablesExist(self):
        self.Connect()
        cursor = self.Connection.cursor()
        # Have not looked up the right way to do this. TODO: Fix.
        try:
            cursor.execute('SELECT * FROM {0} LIMIT 1'.format(self.TableMeta))
        except sqlite3.OperationalError as ex:
            # Expected error message: 'no such table: {table_name}'
            econ_platform_core.log_warning('sqlite3 error %s', ex)
            if self.TableMeta.lower() in ex.args[0].lower():
                raise econ_platform_core.entity_and_errors.PlatformError('Tables do not exist. Need to run the initialisation script init_sqlite.py in the scripts directory.')
            else:
                print(str(ex))
                raise econ_platform_core.entity_and_errors.PlatformError('Error when testing for table existence')

    def Execute(self, cmd, *args, commit_after=False, is_many=False):
        """
        Convenience function that logs commands if self.LogSQL is True.

        :param cmd: str
        :param args:
        :param commit_after: bool
        :return: sqlite3.Cursor
        """
        if self.Connection is None:
            self.Connect()
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
        self.Connect()
        search_query = 'SELECT COUNT(*) FROM {0} WHERE ticker_full = ?'.format(self.TableMeta)
        cursor = self.Execute(search_query, str(series_meta.ticker_full))
        res = cursor.fetchall()
        return res[0][0] > 0

    def Retrieve(self, series_meta):
        self.Connect()
        ticker_full = str(series_meta.ticker_full)
        series_id = self.GetSeriesID(ticker_full)
        if series_id is None:
            raise econ_platform_core.entity_and_errors.TickerNotFoundError('{0} not found on database'.format(ticker_full))
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
            raise econ_platform_core.entity_and_errors.PlatformError('Corrupted date axis for {0}'.format(ticker_full))
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
        self.Connect()
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
        self.Connect()
        create_str = """
INSERT INTO {0} (series_provider_code, ticker_full, ticker_query, series_name, series_description, frequency,
provider_param_string) VALUES
(?, ?, ?, ?, ?, ?, ?)        
        """.format(self.TableMeta)
        local_ticker = series_meta.ticker_local
        self.Execute(create_str, str(series_meta.series_provider_code), str(series_meta.ticker_full),
                     series_meta.ticker_query, series_meta.series_name , series_meta.series_description,
                     series_meta.frequency,
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
        self.Connect()
        self.Execute(cmd, str(series_meta.ticker_full), commit_after=False)
        if self.Cursor.rowcount > 1:  # pragma: nocover
            # This should never be hit, but it could happen if the SQL command is mangled.
            # Unless cascade deletions are counted...
            raise econ_platform_core.entity_and_errors.PlatformError(
                'Internal Error! Attempted to delete more than one row!')
        if warn_if_non_existent and 0 == self.Cursor.rowcount:
            econ_platform_core.log_warning('Series to be deleted did not exist: {0}'.format(
                str(series_meta.ticker_full)))
        self.Connection.commit()

    def _GetMetaFromFullTicker(self, full_ticker):
        """
        Get the metadata for a full ticker.

        :param full_ticker: econ_platform_core.tickers.TickerFull
        :return: econ_platform_core.SeriesMetadata
        """
        ticker = str(full_ticker)
        mapper = {
            'series_id': 'series_id',
            'series_provider_code': 'series_provider_code',
            'ticker_query': 'ticker_query',
            'series_name': 'series_name',
            'series_description': 'series_description',
            'frequency': 'frequency',
            'provider_param_string': None
        }
        collist = list(mapper.keys())
        # LIMIT 1 is redundant, but...
        res = self.SelectColumnList(self.TableMeta, collist, 'ticker_full = ?', ticker, limit_n=1)
        meta = econ_platform_core.series_metadata.SeriesMetadata()
        meta.ticker_full = full_ticker
        meta.series_provider_code, meta.ticker_query = full_ticker.SplitTicker()
        if len(res) == 0:
            meta.Exists = False
            return meta
        meta.Exists = True
        for c, val in zip(collist, res[0]):
            if mapper[c] is not None:
                meta[mapper[c]] = val
            elif 'provider_param_string' == c:
                meta.ProviderMetadata = econ_platform_core.utils.param_string_to_dict(val)
        return meta


    def SelectColumnList(self, table, column_list, where_str, where_params, limit_n):
        """
        Executes a SELECT statement, returns cursor.fetchall()

        The where_str has to be already formatted with '?' placeholders, without the "WHERE"

        :param table: str
        :param column_list: list
        :param where_str: str
        :param where_params: list
        :param limit_n: int
        :return:
        """
        col_str = ','.join(column_list)
        limit_str = ' LIMIT {0}'.format(limit_n)
        cmd = 'SELECT {0} FROM {1} WHERE {2} {3}'.format(col_str, table, where_str, limit_str)
        self.Connect()
        self.Execute(cmd, where_params)
        return self.Cursor.fetchall()

    def CreateSqlite3Tables(self):
        """
        Can invoke this by running a script in the scripts directory.
        :return:

        """
        self.LogSQL = True
        self.SetParameters()
        full_name = self.DatabaseFile
        self.Connection =  sqlite3.Connection(full_name)
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
        frequency text NULL,
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
        # self.TestTablesExist()
        self.Connection.commit()

    # def _GetLastRefresh(self, ticker_full):
    #     """
    #
    #     :param ticker_full: TickerFull
    #     :return:
    #     """
    #     # TODO: implement this to boost performance. For now, uses superclass's method, which gets the information
    #     # from the SeriesMetadata object (which fills all fields, not just the last_refresh.

    def _SetLastRefresh(self, ticker_full, time_stamp=None):
        """
        Set the last_refresh field.
        :param ticker_full: TickerFull
        :param time_stamp: datetime.datetime
        :return:
        """
        id = self.GetSeriesID(ticker_full)
        cmd = """
        UPDATE {0} SET last_update = ? WHERE id_series = ?""".format(self.TableMeta)
        if time_stamp is None:
            time_stamp = datetime.datetime.now()
        self.Execute(cmd, id, time_stamp, commit_after=True)

    def _SetLastUpdate(self, ticker_full, time_stamp=None):
        """
        Set the last_refresh, last_update field.
        :param ticker_full: TickerFull
        :param time_stamp: datetime.datetime
        :return:
        """
        id = self.GetSeriesID(ticker_full)
        cmd = """
        UPDATE {0} SET last_update = ?, last_refresh = ? WHERE series_id = ?""".format(self.TableMeta)
        if time_stamp is None:
            time_stamp = datetime.datetime.now()
        self.Execute(cmd, id, time_stamp, time_stamp, commit_after=True)




def create_sqlite3_tables():
    """
    Create the tables if they are not in the database file.

    Can be invoked by running the script init_sqlite.py in the scripts directory.

    :return:
    """
    obj = DatabaseSqlite3()
    obj.CreateSqlite3Tables()
    del obj
    obj2 = DatabaseSqlite3()
    obj2.TestTablesExist()


