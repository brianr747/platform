"""
Platform extensions.

Place all modules that extend the platform (including monkey-patching the base code).

This module creates an load_extensions() function that imports *all* python source (*.py) modules in this directory.

Will come up more options (a user-configurable list?) later.

Obviously, use at own risk!


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


import importlib
import os


def load_extensions():
    # There might be some iteration tools in importlib, but no time to read documentation...
    this_dir = os.path.dirname(__file__)
    flist = os.listdir(this_dir)
    exclusion_list = ['__init__']
    loaded_extensions = []
    failed_extensions = []
    for fname in flist:
        fname = fname.lower()
        if not fname.endswith('.py'):
            continue
        fname = fname[:-3]
        if fname in exclusion_list:
            continue
        # Import it!
        try:
            mod = importlib.import_module('myplatform.extensions.' + fname)
            if hasattr(mod, 'extension_name'):
                fname = str(mod.extension_name)
            # Try running main()
            if hasattr(mod, 'main'):
                mod.main()
            print('Extension {0} loaded.'.format(fname))
            loaded_extensions.append(fname)
        except Exception as ex:
            print('Failure loading extension:', fname)
            print(type(ex), str(ex))
            failed_extensions.append(fname)
    return (loaded_extensions, failed_extensions)