# (c) 2019 Brian Romanchuk
source('startup.R')

inv_sales <- pfetch('F@A812RC2Q027SBEA')
ser <- inv_sales
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              '%', main='U.S.: Ratio Of Nonfarm Inventories To Domestic Business Final Sales',
              startdate = '1947-01-01')
pp <- SetXAxis(pp,"1949-01-01", "2019-05-01")
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)



OnePanelChart(pp, "c20190803_inventory_sales_long.png","Shade indicates NBER recessions. Source: BEA (via FRED).")
