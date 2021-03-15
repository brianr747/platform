

# (c) 2019 Brian Romanchuk
source('startup.R')

tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
recession <- pfetch('F@USREC')
ser <- 100*(tsy10-tsy2)
pp <- Plot1Ser(ser,  
                 ylab="BPs.",main="U.S. Treasury 2-/10-Year Slope", 
                 startdate='2015-01-01')
pp <- SetXAxis(pp, "2015-01-01", "2020-01-01")
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(pp, "c20191020_tsy_2_10_slope.png","Source: Fed H.15 (via FRED).")



