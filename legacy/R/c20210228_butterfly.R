

# (c) 2021 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')

tsy2 <- pfetch('F@DGS2')
tsy5 <- pfetch('F@DGS5')
tsy10 <- pfetch('F@DGS10')

bfly <- 100*(tsy5 - (tsy2 + tsy10)/2)

p2 <- ShadeBars1(bfly["2000-01-01/"],  recession,   
                 ylab="BPs.",main="U.S. Treasury 2/5/10 Butterfly", 
                 startdate='2000-01-01')
p2 <- SetXAxis(p2, "2000-01-01", 3)
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(p2, "cc20210228_butterfly.png","*5-year less 50-50 2-10-year barbell. Source: Fed H.15 via FRED.")


