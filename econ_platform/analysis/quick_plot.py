"""
quick_plot.py

As the name suggests, quickly plot a series...

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


import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def quick_plot(ser, title=None):  # pragma: nocover  No sensible way to cover this unless it is turned into a class
    """
    There's some overhead with plotting...
    :param ser: pandas.Series
    :return:
    """
    if plt is None:
        raise ImportError('Was not able to import plotting libraries (matplotlib.pyplot) or the converter.')
    plt.plot(ser)
    if title is None:
        title = ser.name
    plt.title(title)
    plt.grid(True)
    plt.show()