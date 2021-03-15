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
cpi <- pfetch('F@CPIAUCSL')
inf_avg <- MA(pchange(cpi,12), 120)

pp <- ShadeBars1(break10, recession, '%', 'U.S. 10-Year Inflation Breakeven',
                 startdate='2004-01-01')
pp <- SetXAxis(pp, "2004-01-01", 2)

p2 <- ShadeBars2(inf5_5, inf_avg, recession, c('5Y/5Y Breakeven', '10-Year Moving Average Headline'), 
                 '%', 'U.S. Forward Inflation Versus Average',
                 startdate='2004-01-01', legendhead='Inflation', legendpos=c(.8, .85))
p2 <- SetXAxis(p2, "2004-01-01", 2)

OnePanelChart(pp, "c20201216_10y_breakeven.png","Shade represents recessions. Source: H.15, St. Louis Fed.")



OnePanelChart(p2, "c20201216_breakeven_vs_historic.png","Shade represents recessions. Source: H.15, St. Louis Fed.")


