# (c) 2019 Brian Romanchuk
source('startup.R')

RGDP <- pfetch('F@GDPC1')
recession <- pfetch('F@USREC')

tsy5 <- pfetch('F@DGS5')
tsy10 <- pfetch('F@DGS10')
frd <- (1 + tsy10/100)^2/(1+tsy5/100)
frd <- 100*(frd-1)

ser <- frd
pp <- ShadeBars2(tsy5, ser, recession, legend = c('Spot', '5-Years Forward'),
              '%', main='U.S. 5-Year Treasury Spot And Forward Rates',
              startdate = '1990-01-01', legendhead = '5-Year')
pp <- SetXAxis(pp,"1990-01-01", 4)
#pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(pp,"c20191211_tsy_spot_frd.png","Recessions shaded. Source: Fed H.15 (via FRED), author calculations.")
