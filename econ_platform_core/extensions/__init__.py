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

import econ_platform_core


# This function will be replaced with straight import statements. Only leaving this dynamic
# since the design is changing rapidly at this stage. Once the core has stabilised, we will just import
# the "core extensions". As a result, no point in figuring out unit test techniques.
# Also: may create a "ExtensionManager" class to do this work.


class ExtensionManager(econ_platform_core.PlatformEntity):
    """
    Class to handle extension loading and status. Currently non-functional; code will migrate to using this.

    This class just offers the interface (for code completion purposes; the real extension manager will be
    defined in extensions.__init__.py
    """

    def __init__(self):
        super().__init__()
        self.LoadedExtensions = []
        self.FailedExtensions = []
        self.DecoratedFailedExtensions = []


def load_extensions():  # pragma: nocover
    """
    Imports all *.py files in this directory (in alphabetical order).

    Since the order of import will eventually matter, will need to add something to force a order of import operations.
    For now, not am issue (can just use the alphabetical order rule to fix problems).

    All errors are caught and largely ignored (other than listing the module that failed, and a text dump on the
    console.

    Returns [loaded_extensions, failed_extensions]

    The operations on import of an extension:

    (1) The import itself. If you wish, you can just put a script that is executed.
    (2) If the module has a variable (hopefully a string) with the name 'extension_name', that is used as the extension
    name for display, otherwise it is the name of the text file.
    (3) If the module has a main() function, it is called.

    Since logging is not yet initialised, things are dumped to console rather than logged. (If you really need logging
    for debugging purposes, you could turn on logging in the extension.)

    :return: list
    """
    # There might be some iteration tools in importlib, but no time to read documentation...
    this_dir = os.path.dirname(__file__)
    flist = os.listdir(this_dir)
    # Do alphabetical order
    flist.sort()
    exclusion_list = ['__init__']
    loaded_extensions = []
    failed_extensions = []
    decorated_fails = []
    use_monkey_example = econ_platform_core.PlatformConfiguration['Options'].getboolean('UseMonkeyPatchExample')
    use_example_provider = econ_platform_core.PlatformConfiguration['Options'].getboolean('UseExampleProvider')
    if not use_monkey_example:
        exclusion_list.append('monkey_patch_example')
    if not use_example_provider:
        exclusion_list.append('hook_provider_example')
    for fname in flist:
        fname = fname.lower()
        if not fname.endswith('.py'):
            continue
        fname = fname[:-3]
        if fname in exclusion_list:
            continue
        # Import it!
        try:
            mod = importlib.import_module('econ_platform_core.extensions.' + fname)
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
            decorated_fails.append((fname, str(ex)))
    return (loaded_extensions, failed_extensions, decorated_fails)