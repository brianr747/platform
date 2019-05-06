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

import myplatform
import myplatform.utils

class DatabaseSqlite3(myplatform.DatabaseManager):
    Cursor: sqlite3.Cursor
    Directory: str
    Connection: sqlite3.Connection

    def __init__(self):
        """
        Initialise the object. Note: Does nothing, including looking up configuration information.

        """
        super().__init__()
        self.Name = 'SQLite Database'
        self.Directory = ''
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
        full_name = os.path.join(self.Directory, self.DatabaseFile)
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
        info = [('Directory', 'directory'),
                ('DatabaseFile', 'file_name'),
                ('MetaTable', 'meta_table'),
                ('DataTable', 'data_table')]
        for attrib, config_name in info:
            # If len() > 0, then already set
            if len(getattr(self, attrib)) == 0:
                # Can either be under "SQL" or "D_SQLITE3"
                try:
                    setattr(self, attrib, myplatform.PlatformConfiguration['SQL'][config_name])
                except KeyError:
                    setattr(self, attrib, myplatform.PlatformConfiguration['D_SQLITE'][config_name])
        # Directory is a special case.
        if self.Directory == 'myplatform':
            self.Directory = myplatform.utils.get_platform_directory()


    def TestTablesExist(self):
        cursor = self.Connection.cursor()
        # If the meta table is there, so it the values table?
        # Don't know how to validate existence of SQL objects, so do it this way
        try:
            cursor.execute('SELECT * FROM {0} LIMIT 1'.format(self.MetaTable))
        except sqlite3.OperationalError as ex:
            # Expected error message: 'no such table: {table_name}'
            myplatform.log_warning('sqlite3 error %s', ex)
            if self.MetaTable.lower() in ex.args[0].lower():
                raise myplatform.PlatformError('Tables do not exist. Need to run the initialisation script init_sqlite.py in the scripts directory.')
            else:
                print(str(ex))
                raise myplatform.PlatformError('Error when testing for table existence')

    def Execute(self, cmd, *args, commit_after=False):
        """
        Convenience function that logs commands if self.LogSQL is True.

        :param cmd: str
        :param args:
        :param commit_after: bool
        :return:
        """
        if self.Connection is None:
            self.GetConnection(test_tables=False)
        if self.Cursor is None:
            self.Cursor = self.Connection.cursor()
        if self.LogSQL:
            if len(args) > 0:
                myplatform.log(cmd + " : " + str(args))
            else:
                myplatform.log(cmd)
        if len(args) > 0:
            self.Cursor.execute(cmd, args)
        else:
            self.Cursor.execute(cmd)
        if commit_after:
            self.Connection.commit()

    def Exists(self, ticker):
        raise NotImplementedError('boum')

    def Retrieve(self, ticker):
        if self.Connection is None:
            self.GetConnection()
        raise NotImplementedError('boum')

    def Write(self, ser, ticker):
        """

        :param ser: pandas.Series
        :param ticker: str
        :return:
        """
        raise NotImplementedError('boum')

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





def _main():
    # test code
    obj = DatabaseSqlite3()
    obj.GetConnection()
    obj.TestTablesExist()


if __name__ == '__main__':
    _main()