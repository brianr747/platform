source('basefn2.R', encoding='UTF-8')


ser2 = pfetch('RBAXLS@FCMYGBAG2D')
ser10 =pfetch('RBAXLS@FCMYGBAG10D')
ser3m = pfetch('RBAXLS@FIRMMBAB90D')

ser <- 100*(ser10 - ser3m)

ser <- ser["1995-01-01/"]
p2 <- PlotLowLevel1(ser, "BPs.","Australian 3-Month/10-Year Slope*")
p2 <- SetXAxis(p2,"1995-01-01", 2)
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)


PlotFromLowLevel(p2,"c20190513_australian_slope.png",
                 "*3-month=bank accepted bills. Source: Reserve Bank of Australia")

GDP <- pfetch('D@OECD/QNA/AUS.B1_GE.VIXOBSA.Q')

gdp_grow <- 2*pchange(GDP,2)

pp <- PlotLowLevel1(gdp_grow["1990-01-01/"], 'Ann % Chg', 'Australian GDP Growth Rate (6-months, Annualised)')
pp <- SetXAxis(pp,"1990-01-01", 2)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

PlotFromLowLevel(pp,"c20190513_australia_GDP.png",
                 "Source: OECD, via DB.nomics")
