"""
tickers.py

Note: I created this module as a reminder to myself that we need to
refactor ticker management into classes. Not yet used.

The defaults are set into this module. The platform initialisation code
can override these defaults at start up. By not looking up the defaults,
there are no imports in this module, which makes life much easier for the import
dependency spaghetti problem faced by the platform.

Users that override the defaults will need to make sure that default initialisation code is invoked
before using this module, as otherwise behaviour will revert to default.

Since almost no code other than unit tests will function without initialising the configuration, this
should not catch too many people.


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


class InvalidTickerError(Exception):
    pass


class _TickerAbstract(object):
    """
    Abstract base class. Should never be instantiated, since whenever we create a ticker, we need to
    know what type it is. The only challenge is when we get a string from an external source (e.g., a user
    fetch() command, in which case we need to map the raw str object to one of the ticker sub-classes.
    """
    def __init__(self, txt=''):
        self.Text = str(txt)
        # This will blow up for the base class!
        self.AssertValid()

    def __str__(self):
        return self.Text

    def __len__(self):
        return len(self.Text)

    def IsValid(self):
        """
        Should not be instantiating these objects.
        :return:
        """
        return False

    def AssertValid(self):
        if not self.IsValid():
            raise InvalidTickerError('{0} not a valid ticker for this ticker type {1}'.format(self.Text,
                                                                                              type(self)))


class TickerFull(_TickerAbstract):
    """
    Tickers of the form {provider code}[Delimiter]{external fetch ticker}.

    Delimiter = '@' by default.

    """
    DelimiterSplit = '@'

    def IsValid(self):
        return TickerFull.DelimiterSplit in self.Text

    def SplitTicker(self):
        """
        Split the ticker into [{provider_code}, {external_fetch_ticker}].
        :return: list
        """
        try:
            s1, s2 = self.Text.split(TickerFull.DelimiterSplit, 1)
            return TickerProviderCode(s1), TickerFetch(s2)
        except:  # pragma: nocover
            # Probably should not get here.
            raise InvalidTickerError('{0} is not a valid full ticker; cannot be split'.format(self.Text))


class _TickerNotFullTicker(_TickerAbstract):
    """
    This strangle little class is a bit of a place holder. Will be used as a stand-in for some not-yet-implemented
    ticker types. The only defining characteristic is that it is not a "full ticker". That is, there are no
    TickerFull.DelimiterSplit characters in it.

    A couple of the classes directly inherit from this class, but they may have more intricate validations later.
    """
    def IsValid(self):
        """
        Right now, just making sure there are no reserved characters. Should not have things like spaces either.
        :return: bool
        """
        return not TickerFull.DelimiterSplit in self.Text

class TickerProviderCode(_TickerNotFullTicker):
    """
    Is this a valid Provider ticker?

    Right now, the only constraint is that it does not qualify as a "full ticker"; may add
    extra validation code later.
    """
    pass


class TickerLocal(_TickerNotFullTicker):
    """
    "Local tickers" are local aliases that have one key feature: they do not qualify as full tickers.

    When parsing externally-supplied strings, the main effort is splitting them between a "full ticker"
    and local tickers. (A variant of local tickers may be added, which are in a "entity|data_type" format.
    """
    pass


class TickerDataType(_TickerAbstract):
    """
    This class is not supported yet, but will have the format {entity_ticker}[delimiter]{data_type}.

    Cannot have a TickerFull.DelimiterSplit character.

    """
    DelimiterData = '|'

    def IsValid(self):
        """
        Current rules.

        (1) Cannot qualify as a "full ticker" (not TickerFull.DelimiterSplit ("@")
        (2) Contains at least one DelimiterData character.

        :return: bool
        """
        return (TickerFull.DelimiterSplit not in self.Text) and (TickerDataType.DelimiterData in self.Text)


class TickerFetch(_TickerAbstract):
    """
    Tickers used by providers in external fetch commands.

    No real restrictions, because who knows what those people will do?

    (We don't want to burden people with escaping reserved characters.)
    """
    def IsValid(self):
        """
        The awkward thing about external tickers is that they are almost always valid.

        Only test: is the ticker non-empty?
        :return: bool
        """
        return len(self.Text) > 0


def map_string_to_ticker(ticker):
    """
    Convert a raw string object into a ticker class object.

    Should be called against strings supplied from the public interface functions; internal code sticks
    to the correct objects.

    The testing hierarchy is as-follows.

    (1) If it qualifies as a full ticker, return TickerFull
    (2) Try to see if it is a datatype ticker.
    (3) If not, it is a local ticker.

    :param ticker: str
    :return: _TickerAbstract
    """
    # Force to a string.
    ticker = str(ticker)
    if len(ticker) == 0:
        raise InvalidTickerError('Tickers cannot be empty strings')
    try:
        return TickerFull(ticker)
    except InvalidTickerError:
        try:
            return TickerDataType(ticker)
        except InvalidTickerError:
            return TickerLocal(ticker)


def create_ticker_full(ticker_provider, ticker_fetch):
    """
    Create a TickerFull object from provider and fetch ticker.

    :param ticker_provider: str
    :param ticker_fetch: str
    :return: TickerFull
    """
    ticker_str = '{0}{1}{2}'.format(str(ticker_provider), TickerFull.DelimiterSplit, str(ticker_fetch))
    return TickerFull(ticker_str)
