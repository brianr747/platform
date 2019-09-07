# (c) 2019 Brian Romanchuk
source('startup.R')

ur <- pfetch('F@UNRATE')
recession <- pfetch('F@USREC')
ur_3 <- MA(ur, 3)
ur_lag = lag(ur_3, 1)
ur_min <- rollapply(ur_lag, 12, min)


ser = ur - ur_min
ser_us <- ser
pp <- ShadeBars1(ser, recession, 
              '%', main='Sahm Trigger Rule: U.S. Unemployment Rate* And Recessions**',
              startdate = '1970-01-01')
pp <- SetXAxis(pp,"1970-01-01", "2019-01-01")
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
pp <- pp + geom_hline(yintercept=0.5,color="red",size=1, linetype=3)
OnePanelChart(pp,"c20190608_sahm_trigger_us.png","*3-mo m.a. **NBER definition. Source: BLS (via FRED).")

#----------------------------------------------------

ca_recession = pfetch('U@CANADIAN_RECESSIONS')
ca_UR <- pfetch('STATCAN@14100287|v2062815')

ur_3 <- MA(ca_UR, 3)
ur_lag = lag(ur_3, 1)
ur_min <- rollapply(ur_lag, 12, min)

ser = ca_UR - ur_min
pp <- ShadeBars1(ser, ca_recession, 
                 '%', main='Sahm Trigger Rule: Canadian Unemployment Rate* And Recessions**',
                 startdate='1977-03-01')
pp <- SetXAxis(pp,"1977-03-01", "2019-01-01")
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
pp <- pp + geom_hline(yintercept=0.5,color="red",size=1, linetype=3)
OnePanelChart(pp,"c20190608_sahm_trigger_ca.png","*3-mo m.a. **C.D. Howe definition. Source: Statscan.")

#-----------------------------------------------------

devn_trend <- ur - MA(ur, 12)

pp <- ShadeBars2(devn_trend, ser_us, recession, ylab='%', startdate='1970-01-01',
                 main='U.S. Unemployment Rate Indicators', legend=c('Deviation from Trend',
                  'Sahm Trigger Rule'), legendhead='Unemployment Deviation', legendpos=c(.5, .8))

pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
OnePanelChart(pp,"c20190608_ur_indicator_comparison.png","Source: BLS (via FRED).")
#-----------------------------------------------------------

emratio <- pfetch('F@EMRATIO')

pp <- ShadeBars1(emratio, recession, 
                 '%', main='U.S. Employment-To-Population Ratio And Recessions*',
                 startdate = '1950-01-01')
pp <- SetXAxis(pp,"1950-01-01", "2019-01-01")


em_3 <- MA(emratio, 3)
em_max <- rollapply(em_3, 13, max)

devn <- em_3 - em_max
p2 <- ShadeBars1(devn, recession, 
                 '%', main='Trigger Indicator Based On Employment Ratio And Recessions*',
                 startdate = '1970-01-01')
p2 <- SetXAxis(p2,"1970-01-01", "2019-01-01")
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
#pp <- pp + geom_hline(yintercept=0.5,color="red",size=1, linetype=3)


TwoPanelChart(pp, p2, "c20190608_emratio.png","*NBER definition. Source: BLS (via FRED).")

