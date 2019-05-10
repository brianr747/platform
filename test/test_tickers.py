
import unittest

import econ_platform_core.tickers as tickers


class TestTickers(unittest.TestCase):

    def is_equal(self, a, b):
        self.assertEqual(a.Text, b.Text)
        self.assertEqual(type(a), type(b))
        return True

    def test_abstract(self):
        with self.assertRaises(tickers.InvalidTickerError):
            tickers._TickerAbstract('cat')

    def test_ticker_full(self):
        tickers.TickerFull.DelimiterSplit = '|'
        tickers.TickerFull('A|B')
        with self.assertRaises(tickers.InvalidTickerError):
            tickers.TickerFull('A@B')
        tickers.TickerFull.DelimiterSplit = '@'
        tickers.TickerFull('A@B')

    def test_str(self):
        x = tickers.TickerFull('A@B')
        self.assertEqual('A@B', str(x))

    def test_len(self):
        x = tickers.TickerFull('A@B')
        self.assertEqual(3, len(x))

    def test_split(self):
        x = tickers.TickerFull('A@B')
        [a,b] = x.SplitTicker()
        self.is_equal(tickers.TickerProviderCode('A'), a)
        self.is_equal(tickers.TickerFetch('B'), b)

    def test_datatype(self):
        tickers.TickerFull.DelimiterSplit = '@'
        tickers.TickerDataType.DelimiterData = '|'
        tickers.TickerDataType('A|B')
        with self.assertRaises(tickers.InvalidTickerError):
            tickers.TickerDataType('A@B|B')
        with self.assertRaises(tickers.InvalidTickerError):
            tickers.TickerDataType('ABV')

    def test_map_string(self):
        with self.assertRaises(tickers.InvalidTickerError):
            tickers.map_string_to_ticker('')
        self.is_equal(tickers.TickerFull('A@B'), tickers.map_string_to_ticker('A@B'))
        self.is_equal(tickers.TickerFull('A@B|C'), tickers.map_string_to_ticker('A@B|C'))
        self.is_equal(tickers.TickerDataType('A|B'), tickers.map_string_to_ticker('A|B'))
        self.is_equal(tickers.TickerLocal('AB'), tickers.map_string_to_ticker('AB'))



