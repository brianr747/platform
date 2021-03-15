# (c) 2019 Brian Romanchuk
source('startup.R')


RGDP <- pfetch('F@GDPC1')
recession <- pfetch('F@USREC')
ser <- pchange(RGDP, 4)
pp <- ShadeBars1(ser, recession, 
                 'Ann % Chg', main='U.S. Real GDP Growth Rate And Recessions*',
                 startdate = '1980-01-01')
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

pp <- SetXAxis(pp, "1980-01-01", 4)


tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')

ser <- 100*(tsy10-tsy2)

p2 <- ShadeBars1(ser, recession, 
              '', main='U.S. 2-/10-Year Treasury Slope',
              startdate = '1980-01-01')
p2 <- SetXAxis(p2,"1980-01-01", 4)
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp,p2, "c20191204_GDP_slope.png","Sources: BEA, Fed H.15 (via FRED).")

