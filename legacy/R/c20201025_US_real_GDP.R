

# (c) 2019 Brian Romanchuk
source('startup.R')


ser <- pfetch('F@GDPC1')
recession <- pfetch('F@USREC')

p2 <- ShadeBars1(ser, recession, 
               ylab="",main="U.S. Real GDP", 
               startdate='1980-01-01')
p2 <- SetXAxis(p2, "1980-01-01", 5)

OnePanelChart(p2, "c20201025_US_real_GDP.png","Source: BEA (via FRED).")



