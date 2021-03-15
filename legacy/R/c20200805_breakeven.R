source('startup.R')


recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
pp <- ShadeBars1(ff,  recession,  
                 ylab="%",main="U.S. Federal Funds Target Rate*", 
                 startdate='1984-01-01')
pp <- SetXAxis(pp, "1984-01-01", 4)


tsy10 <- pfetch('F@DGS10')
tips10 <- pfetch('F@DFII10')
break10 <- tsy10 - tips10
inf5_5 <-pfetch('F@T5YIFR')

pp <- ShadeBars1(break10, recession, '%', '10-Year Inflation Breakeven',
                 startdate='2004-01-01')
pp <- SetXAxis(pp, "2004-01-01", 4)

p2 <- ShadeBars1(inf5_5, recession, '%', '5-Year Inflation Breakeven, 5-Years Forward',
                 startdate='2004-01-01')
p2 <- SetXAxis(p2, "2004-01-01", 4)

TwoPanelChart(pp,p2, "c20200805_breakeven.png","Shade represents recessions. Source: H.15, St. Louis Fed.")


