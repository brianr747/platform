# (c) 2019 Brian Romanchuk
source('startup.R')

real10 <- pfetch('D@BOE/4051/IUMAMRZC')
ser <- real10
pp <- Plot1Ser(ser,  
              '%', main='U.K. 10-Year Real Zero Rate',
              startdate = '1985-01-01')
pp <- SetXAxis(pp,"1985-01-01", 3)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

OnePanelChart(pp, "c20200219_uk_real_10.png","Source: BoE (via DB.nomics).")
