# (c) 2019 Brian Romanchuk
source('startup.R')

auto_inv <- pfetch('F@AISRSA')
ser <- auto_inv
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              '', main='U.S.: Auto Inventory-Sales Ratio',
              startdate = '1993-01-01')
pp <- SetXAxis(pp,"1993-01-01", "2019-06-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
pp <- pp + geom_vline(colour="red", xintercept=as.numeric(as.Date("2017-01-01")))
pp <- pp + annotate("text",x=as.Date("2016-01-01"),y=3.5,size=2,label="Jan\n2017")


prod <- pfetch('F@DAUPSA')
ser <- prod
p2 <- ShadeBars1(ser, recession, 
                 'Thous', main='U.S.: Domestic Auto Production',
                 startdate = '1993-01-01')
p2 <- SetXAxis(p2,"1993-01-01", "2019-06-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
p2 <- p2 + geom_vline(colour="red", xintercept=as.numeric(as.Date("2017-01-01")))
p2 <- p2 + annotate("text",x=as.Date("2016-01-01"),y=500,size=2,label="Jan\n2017")

TwoPanelChart(pp,p2, "c20190803_auto_inventory.png","Shade indicates NBER recessions. Source: BEA (via FRED).")
