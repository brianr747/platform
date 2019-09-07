# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')

tsy10 <- pfetch('F@DGS10')
tips10 <- pfetch('F@DFII10')
ser <- tsy10 - tips10
pp <- Plot1Ser(ser,  recession,  
                 ylab="%",main="U.S. 10-Year Breakeven Inflation Rate", 
                 startdate='2012-01-01')
pp <- SetXAxis(pp, "2012-01-01", 2)

OnePanelChart(pp, "c20190801_2_breakeven.png","Source: Fed H.15 (via FRED).")

