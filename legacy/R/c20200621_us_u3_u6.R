# (c) 2019 Brian Romanchuk
source('startup.R')

u3 <- pfetch('F@UNRATE')
u6 <- pfetch('F@U6RATE')
ser <- u3
ser2 <- u6
recession <- pfetch('F@USREC')
pp <- ShadeBars2(ser, ser2, recession, c('Headline (U-3)', 'U-6'),
              '%', main='U.S.: Unemployment And Underemployment Rates',
              startdate = '1980-01-01', legendpos = c(.2, .8), 
              legendhead = 'Unemployment Rate')
pp <- SetXAxis(pp,"1980-01-01", 5)

OnePanelChart(pp,"c20200621_us_u3_u6.png","Shade indicats NBER recessions. Source: BLS (via FRED).")
