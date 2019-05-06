"""
Script to initialise the sqlite3 database. Needs to be run before using the database file
"""

import os

import myplatform.databases.database_sqlite3



def main():
    myplatform.LogInfo.LogDirectory = os.path.dirname(__file__)
    myplatform.start_log()
    myplatform.log('Starting')
    print('Initialising the SQLite database')
    print('If they exist, will throw an error.')
    try:
        myplatform.databases.database_sqlite3.create_sqlite3_tables()
    except:
        myplatform.log_last_error()
        raise

if __name__ == '__main__':
    main()