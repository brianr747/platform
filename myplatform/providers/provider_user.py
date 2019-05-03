"""
Provider for internally generated series.

By default, empty, but the idea is that you push your own handlers into this object. Probably need to monkey-patch
your own class if this gets complicated.

"""

import myplatform


class ProviderUser(myplatform.ProviderWrapper):
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


    def fetch(self, query_ticker):
        """
        Get a series
        :param query_ticker: str
        :return: list
        """
        fn = self.MapTicker(query_ticker)
        ser = fn(query_ticker)
        ser.name = '{0}@{1}'.format(self.ProviderCode, query_ticker)
        return [ser,]
