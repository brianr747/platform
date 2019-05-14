import loc_utils

# loc_utils.skip_this_extension_module()

import pandas
import unittest
import time
import datetime

import econ_platform_core.databases.database_sqlite3 as database_sqlite3


class TestEndToEnd(unittest.TestCase):
    def test_write(self):
        # Note that there is a lot going under the hood here...
        loc_utils.use_test_configuration()
        # In order to be unique, get time as a number of seconds.
        targ = time.time()
        ddate = datetime.date.today()
        ser = pandas.Series(targ)
        ser.index = pandas.Series(ddate)
        obj = database_sqlite3.DatabaseSqlite3()
        meta = obj.Find('TEST@test_write_1')
        obj.Write(ser, meta)
        ser2 = obj.Retrieve(meta)
        self.assertEqual(ser2.index[0], ser.index[0])
        self.assertEqual(ser2.values[0], ser.values[0])
        self.assertEqual(1, len(ser2.values))



