# (c) 2019 Brian Romanchuk
source('startup.R')

cfnai <- pfetch('F@CFNAI')
ser <- MA(cfnai, 3)
ser2 <- MA(ser, 120)
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              '%', main='U.S.: Chicago Fed National Activity Index (3-month M.A.)',
              startdate = '1968-01-01')
pp <- SetXAxis(pp,"1968-01-01", "2025-01-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

OnePanelChart(pp,"c20190710_CFNAI.png","Shade indicats NBER recessions. Source: Chicago FRB (via FRED).")
