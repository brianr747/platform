

# (c) 2019 Brian Romanchuk
source('startup.R')

boc_assets <-pfetch('STATCAN@10100136|v36610')
gcan_deposit <- pfetch('STATCAN@10100136|v36628')
notes <- pfetch('STATCAN@10100136|v36625')


ser <- 100*notes/boc_assets
ser2 <- 100*(notes+gcan_deposit)/boc_assets

pp <- Plot2Ser(ser, ser2, c('Currency Notes', 'Notes Plus Federal Deposit'),
                 ylab="%",main="Bank of Canada: Traditional Liabilities", 
                 startdate='2012-01-01', legendhead = 'Liability',
               legendpos =c(.2, .2))
pp <- SetXAxis(pp, "2012-01-01", "2019-12-31")

banks <- pfetch('STATCAN@10100136|v36636')

ser <- 100*banks/boc_assets
p2 <- Plot1Ser(ser, 
               ylab="%",main="Bank of Canada: Bank Balances As % Of Balance Sheet", 
               startdate='2012-01-01')
p2 <- SetXAxis(p2, "2012-01-01", "2019-12-31")

TwoPanelChart(pp, p2, "c20201016_boc_liabilities.png","Source: Bank of Canada (via CANSIM).")



