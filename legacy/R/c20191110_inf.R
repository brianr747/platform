

# (c) 2019 Brian Romanchuk
source('startup.R')

cpi <- pfetch('F@CPIAUCSL')
inf <- pchange(cpi,12)


ser <- inf
pp <- Plot1Ser(ser,  
                 ylab="Ann % Chg",main="U.S. Headline Inflation Rate", 
                 startdate='2010-01-01')
pp <- SetXAxis(pp, "2010-01-01", "2020-01-01")
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(pp, "c20191110_inf.png","Source: BLS (via FRED).")



