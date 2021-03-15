

# (c) 2019 Brian Romanchuk
source('startup.R')

cpi <- pfetch('F@CPIAUCSL')
us_core_level <-pfetch('F@CPILFESL')
us_core <- pchange(us_core_level, 12)
inf <- pchange(cpi,12)

can <- pfetch('STATCAN@18100256|v112593702')
can_core = pchange(can,12)

ser <- us_core
pp <- Plot2Ser(ser, can_core, legend=c('U.S. CPI', 'Canada*'), 
                 ylab="Ann % Chg",main="North American Core Inflation Rates", 
                 startdate='1995-01-01', legendhead="Core Inflation",
               legendpos=c(.8,.8))
pp <- SetXAxis(pp, "1995-01-01", 3)
# pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

# CAD <- pfetch('F@DEXCAUS')
# ser <- CAD
# p2 <- Plot1Ser(ser, 'X CAD = 1 USD', main='Canada/U.S. Exchange Rate', 
#                startdate='1995-01-01')
# p2 <- SetXAxis(p2, "1995-01-01", 3)
# 
# CAD_m <- convertdm(CAD)
# ser <- pchange(CAD_m, 12)
# p3 <- Plot1Ser(ser, 'Ann % Chg', main='Canada/U.S. Exchange Rate Percentage Change', 
#                startdate='1995-01-01')
# p3 <- SetXAxis(p3, "1995-01-01", 3)
# p3 <- p3 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(pp,  "c20210104_us_can_inf.png","* Excluding 8 volatile items. Source: BLS, Statscan.")




