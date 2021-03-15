# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
pp <- ShadeBars1(ff,  recession,  
                 ylab="%",main="U.S. Federal Funds Target Rate*", 
                 startdate='1992-01-01')
pp <- SetXAxis(pp, "1992-01-01", 4)


tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')

ser <- 100*(tsy10-tsy2)

p2 <- ShadeBars1(ser, recession, 
              '', main='U.S. 2-/10-Year Treasury Slope',
              startdate = '1992-01-01')
p2 <- SetXAxis(p2,"1992-01-01", 4)
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp,p2, "c20191201_fed_funds_slope.png","*Average of upper and lower limits. Source: Fed H.15 (via FRED).")

