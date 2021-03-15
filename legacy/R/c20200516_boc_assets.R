

# (c) 2019 Brian Romanchuk
source('startup.R')

boc_assets <-pfetch('STATCAN@10100136|v36610')

ser <- boc_assets/1000


pp <- Plot1Ser(ser, 
                 ylab="Bn. $",main="Bank of Canada: Total Assets", 
                 startdate='2007-01-01')
pp <- SetXAxis(pp, "2007-01-01", 3)

repos <- pfetch('STATCAN@10100136|v44201362')

ser <- 100*repos/boc_assets
p2 <- Plot1Ser(ser, 
               ylab="%",main="Bank of Canada: Repos As % Of Assets", 
               startdate='2007-01-01')
p2 <- SetXAxis(p2, "2007-01-01", 3)

TwoPanelChart(pp, p2, "c20200516_boc_assets.png","Source: Bank of Canada (via CANSIM).")



