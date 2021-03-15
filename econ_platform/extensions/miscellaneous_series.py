"""
Script to load miscellaneous series from a module.

The module is assumed to have a dictionary SeriesDict which is of the form:

(1) key = <fetch ticker>
(2) value = function handle that calculates the series.

This module will automatically push those series into the User Provider.

The module path is put into the configuration information
[Options]
miscellaneous_series=<full path to module, including .py>

By default, not set. These are series that are installation-specific.

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

import os

import econ_platform_core

extension_name = 'Miscellaneous Series'


def main():
    try:
        full_path = econ_platform_core.PlatformConfiguration['Options']['miscellaneous_series_module']
    except KeyError:
        # not set; no big deal.
        return
    if not os.path.exists(full_path):
        return
    try:
        module = econ_platform_core.utils.loader('miscellaneous', full_path)
    except:
        print(f'Could not import: {full_path}')
        return
    if not hasattr(module, 'SeriesDict'):
        print('Miscellaneous series does not have a dictionary: SeriesDict')
        return
    for k in module.SeriesDict:
        econ_platform_core.Providers.UserProvider.SeriesMapper[k] = module.SeriesDict[k]