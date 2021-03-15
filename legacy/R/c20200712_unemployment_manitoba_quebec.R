
source('startup.R')


# SA series
#ur_can <- pfetch('STATCAN@14100287|v21581033')
ur_man <- pfetch('STATCAN@14100287|v21581411')
#ur_alb <- pfetch('STATCAN@14100287|v21581519')
ur_qc <- pfetch('STATCAN@14100287|v2065839')
ur_can <- pfetch('STATCAN@14100287|v2064894')
recession = pfetch('U@CANADIAN_RECESSIONS')

pp <- ShadeBars2(ur_man, ur_qc,  recession,  
                 ylab="%",main="Selected Provincial Unemployment Rates",legendpos=c(.2,.8), 
                 startdate='2015-01-01', legend=c('Manitoba', 'Quebec'),
                 legendhead = 'Unemployment Rate (NSA)')
pp <- SetXAxis(pp, "2015-01-01", 1)


OnePanelChart(pp, "c20200712_unemployment_manitoba_quebec.png","Shade represents recession (C.D. Howe). Source: Statscan.")
