

# (c) 2019 Brian Romanchuk
source('startup.R')


tsy10 <- pfetch('F@DGS10')
tips10 <- pfetch('F@DFII10')

ser <- tsy10-tips10
pp <- Plot1Ser(ser,  
                 ylab="%",main="U.S. 10-Year Breakeven Inflation Rate", 
                 startdate='2015-01-01')
pp <- SetXAxis(pp, "2015-01-01", 1)
# pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

p2 <- Plot1Ser(tips10, main="U.S. 10-Year TIPS Indexed Yield", 
               startdate="201501-01")
p2 <- SetXAxis(p2, "2015-01-01", 1)

TwoPanelChart(pp, p2, "c20200325_breakeven.png","Source: Fed H.15 (via FRED).")



