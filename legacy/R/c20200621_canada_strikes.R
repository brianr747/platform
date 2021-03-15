source('startup.R')


strikes_full <- pfetch('STATCAN@14100121|v54552187')
strikes_partial <- pfetch('STATCAN@14100121|v54552205')
ser <- MA(strikes_full + strikes_partial,12)


p2 <- PlotLowLevel1(ser, 'Thousands', 'Canada: Hours Lost In Labour Disputes*')
p2 <- SetXAxis(p2, "1977-01-01", 5)
p2 <- p2 + geom_hline(yintercept=500,color=BondEconomicsBlue(),size=1)
p2 <- p2 + geom_vline(colour=BondEconomicsBlue(), xintercept=as.numeric(as.Date("1990-01-01")))

p2 <- p2 + annotate("text",x=as.Date("1982-01-01"),y=425,size=2,label="Floor")
p2 <- p2 + annotate("text",x=as.Date("2015-01-01"),y=575,size=2,label="Ceiling")

OnePanelChart(p2, "c20200621_canada_strikes.png","*12-month moving average. Source: Statscan.")




