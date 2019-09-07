# (c) 2019 Brian Romanchuk
source('startup.R')


tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
slope <- 100 * (tsy10-tsy2)
slope <- convertdm(slope)
slope <- slope['1976-01-01/2018-12-01']
m = mean(slope)
s = sd(slope)
print('mean')
print(m)
print('STDEV')
print(s)
norm_slope <- (slope - m)/s

payrolls <- pfetch('F@PAYEMS')
pay_avg <- MA(payrolls, 12)
ser <- payrolls/pay_avg
ser <- ser['1976-01-01/2018-12-01']
m = mean(ser)
s = sd(ser)
print('mean')
print(m)
print('STDEV')
print(s)
norm_emp <- (ser - m)/s

recession <- pfetch('F@USREC')
pp <- ShadeBars2(norm_slope, norm_emp, recession, c('2-/10-slope', 'Employment'),
              '', main='U.S.: Two Standardised Indicators',
              startdate = '1977-01-01', legendhead = 'Indicator',
              legendpos=c(.4, .25))
pp <- SetXAxis(pp,"1977-01-01", "2018-12-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


combined = (norm_slope + norm_emp)/2

p2 <- ShadeBars1(combined, recession, 
                 '', main='U.S.: Combined Indicator',
                 startdate = '1977-01-01')
p2 <- SetXAxis(p2,"1977-01-01", "2018-12-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
TwoPanelChart(pp,p2, "c20190710_5_combined_indicator.png","Author calculations. Sources: Fed, BLS (downloaded via FRED).")

