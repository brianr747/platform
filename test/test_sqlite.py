"""

SQLite database testing.

In order to support ease of development, I am using a database on disk. This way I can follow test-driven
development, and still be able to see what is happening in the database with a database browser.

Will switch over to an in-memory database, which will be faster and more stable for testing (since it
will be recreated from scratch every test run), but we cannot see what is happening with external tools.


"""




import loc_utils

# loc_utils.skip_this_extension_module()

import pandas
import unittest
import time
import datetime

import econ_platform_core.databases.database_sqlite3 as database_sqlite3


class TestEndToEnd(unittest.TestCase):
    def test_create(self):
        loc_utils.use_test_configuration()
        obj = database_sqlite3.DatabaseSqlite3()
        meta = obj.Find('TEST@test_create_1')
        if meta.Exists:
            obj.Delete(meta, warn_if_non_existent=False)
        meta.ProviderMetadata = {'KEY': 'VALUE', 'KEY2': 1}
        obj.CreateSeries(meta)
        meta2 = obj.Find('TEST@test_create_1')
        self.assertTrue(meta2.Exists)
        cmd = """
        SELECT provider_param_string FROM {0} WHERE ticker_full = ?""".format(obj.TableMeta)
        obj.Execute(cmd, 'TEST@test_create_1', commit_after=False)
        res = obj.Cursor.fetchall()
        self.assertIn('|KEY=VALUE|', res[0][0])
        self.assertIn('|KEY2=1|', res[0][0])

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
        meta.series_name = 'Test series test_write_1'
        meta.series_description = 'Series to support test test_write()'
        obj.Write(ser, meta)
        ser2 = obj.Retrieve(meta)
        # Note: the date class is changed!
        self.assertEqual(ser2.index[0].year, ser.index[0].year)
        self.assertEqual(ser2.index[0].month, ser.index[0].month)
        self.assertEqual(ser2.index[0].day, ser.index[0].day)
        self.assertEqual(ser2.values[0], ser.values[0])
        self.assertEqual(1, len(ser2.values))



