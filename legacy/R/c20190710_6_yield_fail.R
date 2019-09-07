# (c) 2019 Brian Romanchuk
source('startup.R')


tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
ser <- tsy10['1970-01-01/1982-12-01']

m = mean(ser)
s = sd(ser)
print('mean')
print(m)
print('STDEV')
print(s)
norm_tsy <- (ser - m)/s

recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession,
              '%', main='U.S.: 10-Year Treasury Yield',
              startdate = '1970-01-01')
pp <- SetXAxis(pp,"1970-01-01", "1982-12-01")
#pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)



p2 <- ShadeBars1(norm_tsy, recession, 
                 '', main='U.S. 10-Year Treasury Yield, Standardised',
                 startdate = '1970-01-01')
p2 <- SetXAxis(p2,"1970-01-01", "1982-12-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
TwoPanelChart(pp,p2, "c20190710_6_yield_fail.png","Author calculations. Sources: Fed H.15 (downloaded via FRED).")

