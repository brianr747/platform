

# (c) 2020 Brian Romanchuk
source('startup.R')

emratio <- pfetch('F@EMRATIO')
M2V <- pfetch('F@M2V')
recession <- pfetch('F@USREC')

ser <- emratio
pp <- ShadeBars1(ser,  recession,  
                 ylab="%",main="U.S. Employment-To-Population Ratio (Recent)", 
                 startdate='2005-01-01')
pp <- SetXAxis(pp, "2005-01-01", 2)

p2 <- ShadeBars1(ser,  recession,  
                 ylab="%",main="U.S. Employment-To-Population Ratio (Longer View)", 
                 startdate='1990-01-01')
p2 <- SetXAxis(p2, "1990-01-01", 5)


TwoPanelChart(pp, p2, "c20200605_us_emratio.png","Source: BLS (via FRED).")



