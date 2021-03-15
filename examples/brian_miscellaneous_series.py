
"""
Brian Romanchuk's miscellaneous series. Used in example code.


To use this file, point
[Options]
miscellaneous_series_module=<path to this file>

However, it makes more sense to create your own file, and use any series from here that you like.

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

import econ_platform


def calc_fed(series_meta):
    """
    Splice together a daily Fed Funds rate from FRED series.

    :param series_meta: econ_platform_core.SeriesMetadata
    :return:
    """
    # Just use series_meta to fill in description
    effective = econ_platform.fetch('F@DFF')
    target = econ_platform.fetch('F@DFEDTAR')
    upper = econ_platform.fetch('F@DFEDTARU')
    downer = econ_platform.fetch('F@DFEDTARL')
    new_target = (upper + downer)/2.
    out = target.combine_first(new_target)
    cut_off = out.index[0]
    out = out.combine_first(effective[:cut_off])
    out.name = 'FedFunds: Long Series'
    series_meta.series_description= 'Combination of Fed Funds (FF) Effect (up to 1982), FF target (to 2008), ' \
                                    'then average of upper and lower bounds. '
    series_meta.series_name = 'Fed Funds Long Time History'
    return out, series_meta


SeriesDict = {
    'FedFunds': calc_fed,
}




