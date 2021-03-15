
source('startup.R')


bankrate <- pfetch('STATCAN@10100145|v80691310')
gcan5 <- pfetch('STATCAN@10100145|v80691324')
recession <- pfetch('U@CANADIAN_RECESSIONS')

rng <- '1990-01-01/1995-01-01'
p1 <- ShadeBars2(bankrate[rng], gcan5[rng], recession, '%', main='Canadian Interest Rates In Early 1990s',
                 startdate='1990-01-01', legend=c('Bank Rate', '5-Year GCAN'),
                 legendhead='Rate', legendpos=c(.8,.8))
p1 <- SetXAxis(p1, "1990-01-01", "1995-01-01")



OnePanelChart(p1, "c20200916_canada_yields_crisis.png","Shade represents recession (C.D. Howe). Source: BoC.")
