source('basefn2.R', encoding='UTF-8')

ser <- pfetch("RBAXLS@FCMIYAUG20D", database='SQLITE')

ser <- ser["1997-01-01/"]
p2 <- PlotLowLevel1(ser,"%","Australia Commenwealth Indexed 4% of August 2020")
p2 <- SetXAxis(p2,"1997-01-01", 2)
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

PlotFromLowLevel(p2,"c20190515_acgb_il_2020.png","Source: Reserve Bank of Australia (YieldBroker)")
