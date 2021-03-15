source('startup.R')



ser <- pfetch("D@Eurostat/namq_10_gdp/Q.CP_MEUR.SCA.B1GQ.EL")

ser <- ser["1998-01-01/"]
p2 <- Plot1Ser(ser/1000,"Bn. EUR","Greek Nominal GDP")
p2 <- SetXAxis(p2,"1998-01-01", "2020-01-01")

PlotFromLowLevel(p2,"c20200714_greek_GDP.png","Eurostat via DB.nomics")

