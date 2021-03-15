# (c) 2019 Brian Romanchuk
source('startup.R')


excess <- pfetch('F@EXCSRESNW')
total <- pfetch('F@RESBALNSW')

ser <- 100*(excess/total)
recession <- pfetch('F@USREC')

rng <- '1984-01-01/2000-01-01'
pp <- ShadeBars1(ser[rng], recession[rng], 
              '', main='U.S.: Excess Reserves As % Of Total, Pre-2000',
              startdate = '1980-01-01')
pp <- SetXAxis(pp,"1984-01-01", "2000-06-01")

rng <- '1984-01-01/'
p2 <- ShadeBars1(ser[rng], recession[rng], 
                 '', main='U.S.: Excess Reserves As % Of Total (Until End Of Reserve Requirements)',
                 startdate = '1980-01-01')
p2 <- SetXAxis(p2,"1984-01-01", "2020-06-01")


TwoPanelChart(pp, p2, "c20201124_excess_reserves.png","Shade indicates NBER recessions. Source: H.3 (via FRED).")
