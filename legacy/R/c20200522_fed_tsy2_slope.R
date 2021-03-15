

# (c) 2020 Brian Romanchuk
source('startup.R')

# (c) 2019 Brian Romanchuk
source('startup.R')

tsy2 <- pfetch('F@DGS2')
recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
ser <- 100*(tsy2-ff)
pp <- ShadeBars1(ser,  recession,  
                 ylab="BPs.",main="U.S. 2-Year Yield Spread Over Fed Funds Target Rate*", 
                 startdate='1992-01-01')
pp <- SetXAxis(pp, "1992-01-01", 4)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)


OnePanelChart(pp, "c20200522_fed_tsy2_slope.png","*Midpoint of range. Source: Fed H.15 (via FRED).")



