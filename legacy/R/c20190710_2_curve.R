# (c) 2019 Brian Romanchuk
source('startup.R')

tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
slope <- 100 * (tsy10-tsy2)
slope <- convertdm(slope)
slope <- slope['1976-01-01/2018-12-01']
ser <- slope

recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              'BPs.', main='U.S.: 2-/10-Year Slope',
              startdate = '1977-01-01')
pp <- SetXAxis(pp,"1977-01-01", "2018-12-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


m = mean(slope)
s = sd(slope)
print('mean')
print(m)
print('STDEV')
print(s)
norm_slope <- (slope - m)/s
p2 <- ShadeBars1(norm_slope, recession, 
                 '', main='U.S.: 2-/10-Year Slope, Standardised',
                 startdate = '1977-01-01')
p2 <- SetXAxis(p2,"1977-01-01", "2018-12-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
TwoPanelChart(pp,p2, "c20190710_2_curve.png","Shade indicates NBER recessions. Source: Fed H.15 (via FRED).")

