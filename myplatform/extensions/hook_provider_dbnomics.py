"""
Python script that hooks in the DBnomics code (found in providers).

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

import myplatform
import myplatform.providers.provider_dbnomics

extension_name = 'DB.nomics'

def main():
    """
    Insert the provider into the platform list
    :return:
    """
    obj = myplatform.providers.provider_dbnomics.ProviderDBnomics()
    myplatform.Providers.AddProvider(obj)