# (c) 2019 Brian Romanchuk
source('startup.R')

RGDP <- pfetch('F@GDPC1')
recession <- pfetch('F@USREC')


ser <- pchange(RGDP, 4)
pp <- ShadeBars1(ser, recession,
              'Ann % Chg', main='U.S. Real GDP Growth',
              startdate = '1950-01-01')
pp <- SetXAxis(pp,"1950-01-01", 4)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
pp <- pp + geom_vline(colour="red", xintercept=as.numeric(as.Date("1990-01-01")))

OnePanelChart(pp,"c20200129_us_gdp_long.png","Recessions shaded. Source: BEA (via FRED).")
