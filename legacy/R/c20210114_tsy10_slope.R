# (c) 2021 Brian Romanchuk
source('startup.R')

tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')

pp <- ShadeBars1(tsy10, recession, '%', main='U.S. 10-Year Treasury Yield',
                 startdate='1999-01-01')
pp <- SetXAxis(pp,"1999-01-01", 4)

slope <- 100 * (tsy10-tsy2)
slope <- convertdm(slope)
ser <- slope

recession <- pfetch('F@USREC')
p2 <- ShadeBars1(ser, recession, 
              'BPs.', main='U.S.: 2-/10-Year Slope',
              startdate = '1999-01-01')
p2 <- SetXAxis(p2,"1999-01-01", 4)
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp,p2, "c20210114_tsy10_slope.png","Shade indicates NBER recessions. Source: Fed H.15 (via FRED).")

