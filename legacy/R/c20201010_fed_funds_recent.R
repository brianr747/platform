

# (c) 2020 Brian Romanchuk
source('startup.R')

# (c) 2019 Brian Romanchuk
source('startup.R')

tsy2 <- pfetch('F@DGS2')
recession <- pfetch('F@USREC')
ff <- pfetch('U@FedFunds')
ser <- ff
pp <- ShadeBars1(ser,  recession,  
                 ylab="%.",main="U.S. Fed Funds Target Rate*", 
                 startdate='2013-01-01')
pp <- SetXAxis(pp, "2013-01-01", 1)
#pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)


OnePanelChart(pp, "c20201010_fed_funds_recent.png","*Midpoint of range. Source: Fed H.15 (via FRED).")



