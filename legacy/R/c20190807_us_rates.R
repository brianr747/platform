# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
tsy10 <- pfetch('F@DGS10')
pp <- ShadeBars2(ff, tsy10, recession, c('Federal Funds', '10-Year Treasury'), 
                 ylab="%",main="U.S. Interest Rates", 
                 startdate='1970-01-01', legendhead='Rate:')
pp <- SetXAxis(pp, "1970-01-01", 4)

OnePanelChart(pp, "c20190807_us_rates.png","Source: Fed H.15 (via FRED).")

