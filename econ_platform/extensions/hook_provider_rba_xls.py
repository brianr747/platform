"""
Python script that hooks in the ABSXLS code (found in providers).


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

import econ_platform_core
import econ_platform.providers.provider_rba_xls


extension_name = 'Reserve Bank of Australia (XLS)'

def main():
    """
    Insert the provider into the platform list
    :return:
    """
    obj = econ_platform.providers.provider_rba_xls.ProviderRbaXls()
    econ_platform_core.Providers.AddProvider(obj)