"""

econ_platform: A Python time series analysis support package.


(Note: econ_platform_core contains the core logic of the platform, while this package contains
extension code that use API's outside of the Python standard library, or pandas.


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

# We may restrict this import in the future, but do the "import *" for simplicity during development.
from econ_platform_core import *
import econ_platform.extensions


def quick_plot(ser, title=None):
    """
    Plot a pandas.Series.

    :param ser: pandas.Series
    :param title: str
    :return:
    """
    # This function needs to be left in place.
    _quick_plot_stub(ser, title)

def _quick_plot_stub(ser, title):
    """
    Stub function that should be replaced by analysis.quick_plot.quick_plot()
    by extensions.hook_quick_plot()

    Monkey patching!

    :param ser:
    :param title:
    :return:
    """
    raise PlatformError('quick_plot() not initialised properly; probably matplotlib is not installed.')


def init_core_plus_extensions():
    """
    Call this to initialise the core pcakage, plus add in extensions here.

    (If you just wanted to execute the local extensions only, call econ_platform.extensions.load_extensions()
    :return:
    """
    econ_platform_core.init_package()
    _LoadedExtensions, _FailedExtensions, _DecoratedFailedExtensions = econ_platform.extensions.load_extensions()
    econ_platform_core.LoadedExtensions += _LoadedExtensions
    econ_platform_core.FailedExtensions += _FailedExtensions
    econ_platform_core.DecoratedFailedExtensions += _DecoratedFailedExtensions



