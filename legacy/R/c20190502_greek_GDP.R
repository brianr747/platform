source('basefn2.R', encoding='UTF-8')

ser <- FetchText("D@Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL")

p2 <- PlotLowLevel1(ser/1000,"Bn. EUR","Greek Nominal GDP")
p2 <- SetXAxis(p2,"1997-01-01", 2)

PlotFromLowLevel(p2,"c20190502_greek_GDP.png","Eurostat via DB.nomics")
