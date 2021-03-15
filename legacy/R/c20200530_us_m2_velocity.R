

# (c) 2020 Brian Romanchuk
source('startup.R')

M2V <- pfetch('F@M2V')
recession <- pfetch('F@USREC')

ser <- M2V
pp <- ShadeBars1(ser,  recession,  
                 ylab="",main="U.S. Velocity Of M2 Money Supply", 
                 startdate='1960-01-01')
pp <- SetXAxis(pp, "1960-01-01", 5)


OnePanelChart(pp, "c20200530_us_m2_velocity.png","Source: St. Louis Federal Reserve (via FRED).")



