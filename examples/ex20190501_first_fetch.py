"""
First example of fetching using econ_platform_core

As can be seen, much cleaner analyst interface.

"""


import econ_platform_core
from econ_platform.start import log, fetch, quick_plot




econ_platform_core.configuration.print_configuration(econ_platform_core.PlatformConfiguration)
econ_platform_core.start_log()


def main():
    log('Starting')
    # Need to pre-pend 'D@' to show the provider.
    ser = fetch('D@Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL', database='TEXT')
    # Load the same series multiple times; see the log to see that it is only fetched at most once from
    # the provider
    log('Load loop')
    for i in range(0,10):
        fetch('D@Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL', database='TEXT')
    quick_plot(ser)



if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        log('Error: ' + str(ex))
        raise
