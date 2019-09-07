# (c) 2019 Brian Romanchuk
source('startup.R')

lt <- pfetch('F@LNS13025703')
ser <- lt
ser2 <- MA(ser, 120)
recession <- pfetch('F@USREC')
pp <- ShadeBars2(ser, ser2, recession, c('Current Level', '10-Year Average'),
              '%', main='U.S.: Percentage Of Unemployed That Are Long-Term Unemployed*',
              startdate = '1948-01-01', legendpos = c(.2, .8), 
              legendhead = 'Long-Term Unemployment Proportion')
pp <- SetXAxis(pp,"1948-01-01", "2019-01-01")

OnePanelChart(pp,"c20190706_long_term_unemployment.png","*Greater than 27 weeks. Shade indicats NBER recessions. Source: BLS (via FRED).")
