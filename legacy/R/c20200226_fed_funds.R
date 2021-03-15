source('startup.R')


recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')

tsy10 <- pfetch('F@DGS10')
tips10 <- pfetch('F@DFII10')
break10 <- tsy10 - tips10
tsy5 <- pfetch('F@DGS5')
tips5 <- pfetch('F@DFII5')
break5 <- tsy5 - tips5
inf5_5 <-pfetch('F@T5YIFR')

pp <- ShadeBars2(break5, break10, recession, c('5-Year', '10-Year'), 
'%', 'U.S. Inflation Breakevens',
                 startdate='2004-01-01', legendhead='Inflation Breakeven',
legendpos=c(.7,.35))
pp <- SetXAxis(pp, "2004-01-01", 4)

p2 <- ShadeBars1(inf5_5, recession, '%', '5-Year Inflation Breakeven, 5-Years Forward',
                 startdate='2004-01-01')
p2 <- SetXAxis(p2, "2004-01-01", 4)

TwoPanelChart(pp,p2, "c20200226_breakeven.png","Shade represents recessions. Source: H.15, St. Louis Fed.")


