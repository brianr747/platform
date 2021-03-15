# (c) 2019 Brian Romanchuk
source('startup.R')

tsy10 <- pfetch('F@DGS10')
ff <- pfetch('U@FedFunds')
ser <- tsy10
ser2 <- ff
rng <- "2000-01-01/2015-01-01"
recession <- pfetch('F@USREC')
pp <- ShadeBars2(ser[rng], ser2[rng], recession, c('10-Year Treasury', 'Fed Funds Target'),
              '%', main='No Bond Yield Conundrum Here',
              startdate = '2000-01-01', legendpos = c(.7, .8), 
              legendhead = 'Rate:')
pp <- SetXAxis(pp,"2000-01-01", "2015-01-01")

OnePanelChart(pp,"c20200809_tsy10_conundrum.png","Source: Fed H.15 (via FRED).")
