
import unittest

import econ_platform_core.tickers as tickers


class TestTickers(unittest.TestCase):
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

