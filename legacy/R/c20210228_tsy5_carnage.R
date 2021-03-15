

# (c) 2021 Brian Romanchuk
source('startup.R')

recession <- pfetch('F@USREC')

tsy2 <- pfetch('F@DGS2')
tsy5 <- pfetch('F@DGS5')
tsy10 <- pfetch('F@DGS10')

bfly <- 100*(tsy5 - (tsy2 + tsy10)/2)

p2 <- ShadeBars1(tsy5,  recession,   
                 ylab="%",main="U.S. 5-Year Treasury Yield", 
                 startdate='2018-01-01')
p2 <- SetXAxis(p2, "2018-01-01", "2021-11-01")
# p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(p2, "cc20210228_tsy5_carnage.png","Source: Fed H.15 via FRED.")


