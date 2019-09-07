source('basefn2.R')
source('utils.R')
#source('specialcharts2.R')



ur_can <- pfetch('STATCAN@14100287|v21581033')
ur_man <- pfetch('STATCAN@14100287|v21581411')
ur_alb <- pfetch('STATCAN@14100287|v21581519')
recession = pfetch('U@CANADIAN_RECESSIONS')

pp <- ShadeBars2(ur_can, ur_alb,  recession,  
                 ylab="%",main="Canadian Unemployment Rates And Recessions*",legendpos=c(.2,.8), 
                 startdate='1997-01-01', legend=c('Canada-Wide', 'Alberta'),
                 legendhead = 'Unemployment Rate')
pp <- SetXAxis(pp, "1997-01-01", 4)

# OnePanelChart(pp,"c20190526_canadian_regional_ur.png","*Shade represents recessions (C.D. Howe). Source: Statscan.")


oil <- pfetch('STATCAN@12100128|v1001836062')
p2 <- ShadeBars1(oil, recession, '', main='Crude Oil And Bitumen Export Price Index',
                 startdate='1997-01-01')
p2 <- SetXAxis(p2, "1997-01-01", 4)

TwoPanelChart(pp,p2, "c20190526_canadian_regional_ur.png","*Shade represents recessions (C.D. Howe). Source: Statscan.")
