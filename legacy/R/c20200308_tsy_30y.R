source('startup.R')


recession <- pfetch('F@USREC')

tsy10 <- pfetch('F@DGS10')


p2 <- ShadeBars1(tsy10, recession, '%', '10-Year U.S. Treasury Yield',
                 startdate='1990-01-01')
p2 <- SetXAxis(p2, "1990-01-01", 4)

OnePanelChart(p2, "c20200308_tsy_10y.png","Shade represents recessions. Source: H.15, St. Louis Fed.")


