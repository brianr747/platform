"""
Python script that hooks in the example provider (TEST) code (found in providers).

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
import econ_platform_core.providers.provider_example


extension_name = 'Example Provider (for testing)'

def main():
    """
    Insert the provider into the platform list
    :return:
    """
    obj = econ_platform_core.providers.provider_example.ProviderExample()
    econ_platform_core.Providers.AddProvider(obj)