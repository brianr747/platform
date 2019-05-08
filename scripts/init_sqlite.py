"""
Script to initialise the sqlite3 database. Needs to be run before using the database file
"""

import os

import econ_platform_core.databases.database_sqlite3



def main():
    econ_platform_core.LogInfo.LogDirectory = os.path.dirname(__file__)
    econ_platform_core.start_log()
    econ_platform_core.log('Starting')
    print('Initialising the SQLite database')
    print('If they exist, will throw an error.')
    try:
        econ_platform_core.databases.database_sqlite3.create_sqlite3_tables()
    except:
        econ_platform_core.log_last_error()
        raise

if __name__ == '__main__':
    main()