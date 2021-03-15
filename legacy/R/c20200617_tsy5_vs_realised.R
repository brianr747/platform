
source('startup.R')


source('startup.R')

fed <- pfetch('U@FedFunds')
tsy5 <- pfetch('F@DGS5')

fed_m <- convertdm(fed)
tsy5 <- convertdm(tsy5)
recession <- pfetch('F@USREC')
fed_ma <- MA(fed_m,60)
realised <- lag(fed_ma, k=-60)
realised <- realised["1990-01-01/2015-06-01"]
ser <- tsy5
ser2 <- realised

pp <- ShadeBars2(ser,  ser2, recession, c('Treasury yield', 'realised short rate'),  
                 ylab="%",main="U.S. 5-Year Treasury Versus Realised Short Rate", 
                 startdate='1990-01-01', legendhead='5-year rate')
pp <- SetXAxis(pp, "1990-01-01", "2015-06-01")



gap <- 100 *(tsy5-realised)
p2 <- ShadeBars1(gap, recession, 'BPs.', '5-Year Treasury Yield Less Realised')
p2 <- SetXAxis(p2, "1990-01-01", "2015-06-01")
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

TwoPanelChart(pp, p2, "c20200617_tsy5_vs_realised.png","Source: Fed H.15 (via FRED), author calculations.")


