# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
tsy10 <- pfetch('F@DGS10')
mort30 <- pfetch('F@MORTGAGE30US')
pp <- ShadeBars2(tsy10, mort30, recession, c('10-Year Treasury', '30-Year Mortgage*'), 
                 ylab="%",main="U.S. Interest Rates", 
                 startdate='1990-01-01', legendhead='Rate:')
pp <- SetXAxis(pp, "1990-01-01", 4)

OnePanelChart(pp, "c20190828_us_mortgage.png","*Mortgage data (c) Freddie Mac. Data via FRED.")

