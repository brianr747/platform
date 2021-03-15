
source('startup.R')


recession <- pfetch('F@USREC')
da_balance_sheet <- pfetch('F@WALCL')


#rng <- '1990-01-01/1995-01-01'
p1 <- ShadeBars1(da_balance_sheet/(1000*1000), recession, 'Tn. $', main='U.S. Federal Reserve Balance Sheet: All Assets',
                 startdate='2004-01-01')
p1 <- SetXAxis(p1, "2004-01-01", 3)



OnePanelChart(p1, "c20201004_fed_balance_sheet.png","Shade represents recessions. Source: Fed (via FRED).")
