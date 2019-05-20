"""
Provider for internally generated series.

By default, empty, but the idea is that you push your own handlers into this object. Probably need to monkey-patch
your own class if this gets complicated.

"""

import econ_platform_core


class ProviderUser(econ_platform_core.ProviderWrapper):
    def __init__(self):
        super(ProviderUser, self).__init__(name='User')
        self.SeriesMapper = {}

    def MapTicker(self, query_ticker):
        """
        Monkey patch this method if you have a complex set of user functions
        :param query_ticker: str
        :return:
        """
        try:
            return self.SeriesMapper[str(query_ticker)]
        except KeyError:
            raise econ_platform_core.TickerNotFoundError(
                'There is no function that handles the query ticker: {0}'.format(query_ticker))


    def fetch(self, series_meta):
        """
        Get a series
        :param series_meta: econ_platform_core.SeriesMetadata
        :return: pandas.Series
        """
        query_ticker = series_meta.ticker_query
        fn = self.MapTicker(query_ticker)
        ser = fn(series_meta)
        return ser
