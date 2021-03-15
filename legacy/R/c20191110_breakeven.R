

# (c) 2019 Brian Romanchuk
source('startup.R')


tsy10 <- pfetch('F@DGS10')
tips10 <- pfetch('F@DFII10')

ser <- tsy10-tips10
pp <- Plot1Ser(ser,  
                 ylab="%",main="U.S. 10-Year Breakeven Inflation Rate", 
                 startdate='2017-01-01')
pp <- SetXAxis(pp, "2017-01-01", "2020-01-01")
# pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

p2 <- Plot1Ser(tips10, main="U.S. 10-Year TIPS Indexed Yield", 
               startdate="2017-01-01")
p2 <- SetXAxis(p2, "2017-01-01", "2020-01-01")

TwoPanelChart(pp, p2, "c20191110_breakeven.png","Source: Fed H.15 (via FRED).")



