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
            return self.SeriesMapper[query_ticker]
        except KeyError:
            raise NotImplementedError('There is no function that handles the query ticker: {0}'.format(query_ticker))


    def fetch(self, series_meta):
        """
        Get a series
        :param series_meta: econ_platform_core.SeriesMetaData
        :return: list
        """
        query_ticker = series_meta.ticker_query
        fn = self.MapTicker(query_ticker)
        ser = fn(query_ticker)
        ser.name = series_meta.ticker_query
        return [ser,]
