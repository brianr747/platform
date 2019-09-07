# (c) 2019 Brian Romanchuk
source('startup.R')

contrib <- pfetch('F@A015RY2Q224SBEA')
ser <- contrib
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              '%', main='U.S.: Contribution To Real GDP Growth From Nonfarm Inventories',
              startdate = '1949-01-01')
pp <- SetXAxis(pp,"1949-01-01", "2019-05-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

ser2 <- MA(ser, 4)
p2 <- ShadeBars1(ser2, recession, 
                 '%', main='U.S.: Inventory GDP Contribution, 4 Quarter M.A.',
                 startdate = '1949-01-01')
p2 <- SetXAxis(p2,"1949-01-01", "2019-05-01")
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp,p2, "c20190803_inventory_contrib.png","Shade indicates NBER recessions. Source: BEA (via FRED).")
