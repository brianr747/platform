"""

Hook in quick_plot

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
import econ_platform.analysis.quick_plot

extension_name = 'quick_plot()'

def main():
    """
    Monkey patches econ_platform.analysis.quick_plot() over top of econ_platform._quick_plot_stub()
    :return:
    """
    econ_platform._quick_plot_stub = econ_platform.analysis.quick_plot.quick_plot
