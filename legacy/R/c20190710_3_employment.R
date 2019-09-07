# (c) 2019 Brian Romanchuk
source('startup.R')

payrolls <- pfetch('F@PAYEMS')
# tsy2 <- pfetch('F@DGS2')
#tsy10 <- pfetch('F@DGS10')
#slope <- 100 * (tsy10-tsy2)
#slope <- convertdm(slope)
# slope <- slope['1976-01-01/2018-12-01']
ser <- payrolls/1000
ser <- ser['1976-01-01/2018-12-01']
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              'Millions', main='U.S. Total Nonfarm Employment',
              startdate = '1977-01-01')
pp <- SetXAxis(pp,"1977-01-01", "2018-12-01")
#pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


m = mean(ser)
s = sd(ser)
print('mean')
print(m)
print('STDEV')
print(s)
norm_ser <- (ser - m)/s
p2 <- ShadeBars1(norm_ser, recession, 
                 '', main='U.S.: Total Nonfarm Employment, Standardised',
                 startdate = '1977-01-01')
p2 <- SetXAxis(p2,"1977-01-01", "2018-12-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
TwoPanelChart(pp,p2, "c20190710_3_employment.png","Shade indicates NBER recessions. Source: BLS (via FRED).")

