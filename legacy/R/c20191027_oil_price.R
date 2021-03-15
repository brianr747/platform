# (c) 2019 Brian Romanchuk
source('startup.R')

wti <- pfetch('F@WTISPLC')
ser <- pchange(wti, 12)

recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              'Ann % Chg', main='West Texas Intermediate Crude Price Changes And U.S. Recessions',
              startdate = '1970-01-01')
pp <- SetXAxis(pp,"1970-01-01", 4)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

OnePanelChart(pp,"c20191027_oil_price.png","Shade indicates NBER recessions. Source: St. Louis Fed.")
