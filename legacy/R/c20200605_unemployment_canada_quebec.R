
source('startup.R')


# SA series
#ur_can <- pfetch('STATCAN@14100287|v21581033')
#ur_man <- pfetch('STATCAN@14100287|v21581411')
#ur_alb <- pfetch('STATCAN@14100287|v21581519')
ur_qc <- pfetch('STATCAN@14100287|v2065839')
ur_can <- pfetch('STATCAN@14100287|v2064894')
recession = pfetch('U@CANADIAN_RECESSIONS')

pp <- ShadeBars2(ur_can, ur_qc,  recession,  
                 ylab="%",main="Canadian Unemployment Rates And Recessions*",legendpos=c(.2,.8), 
                 startdate='2005-01-01', legend=c('Canada-Wide', 'Quebec'),
                 legendhead = 'Unemployment Rate (NSA)')
pp <- SetXAxis(pp, "2005-01-01", 4)


OnePanelChart(pp, "c20200605_unemployment_canada_quebec.png","*Shade represents recessions (C.D. Howe). Source: Statscan.")
