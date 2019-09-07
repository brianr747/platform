source('startup.R')



ser <- pfetch("D@Eurostat/bop_gdp6_q/Q.PC_GDP.NSA.CA.BAL.WRL_REST.DE")


p2 <- Plot1Ser(ser,"% of GDP","Germany: Current Account Balance")
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
#

PlotFromLowLevel(p2,"c20190606_germany_current_account.png","Eurostat via DB.nomics")

