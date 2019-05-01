"""
First example of fetching using myplatform

As can be seen, much cleaner analyst interface.

"""



import myplatform
from myplatform import log, fetch
import matplotlib.pyplot as plt

# To turn off a warning...
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

myplatform.start_log()



def main():
    log('Starting')
    # Need to pre-pend 'D@' to show the provider.
    ser = fetch('D@Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL', database='TEXT')
    plt.plot(ser)
    plt.show()



if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        log('Error: ' + str(ex))
        raise
