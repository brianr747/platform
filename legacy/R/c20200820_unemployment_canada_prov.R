
source('startup.R')


# SA series
ur_can <- pfetch('STATCAN@14100287|v21581033')
ur_man <- pfetch('STATCAN@14100287|v21581411')
#ur_alb <- pfetch('STATCAN@14100287|v21581519')
ur_qc <- pfetch('STATCAN@14100287|v2065839')
ur_can <- pfetch('STATCAN@14100287|v2064894')
recession = pfetch('U@CANADIAN_RECESSIONS')

p1 <- ShadeBars1(ur_can, recession, '%', main='Canadian Unemployment Rate (NSA)',
                 startdate='2007-01-01')
p1 <- SetXAxis(p1, "2007-01-01", 1)

pp <- ShadeBars2(ur_man, ur_qc,  recession,  
                 ylab="%",main="Selected Provincial Unemployment Rates",legendpos=c(.2,.8), 
                 startdate='2007-01-01', legend=c('Manitoba', 'Quebec'),
                 legendhead = 'Unemployment Rate (NSA)')
pp <- SetXAxis(pp, "2007-01-01", 1)


TwoPanelChart(p1, pp, "c20200820_unemployment_canada_prov.png","Shade represents recession (C.D. Howe). Source: Statscan.")
