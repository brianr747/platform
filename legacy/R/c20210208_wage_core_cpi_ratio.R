source('startup.R')

u3 <- pfetch('F@UNRATE')
NAIRU <- pfetch('F@NROU')
recession <- pfetch('F@USREC')






us_core_level <-pfetch('F@CPILFESL')
wages <- pfetch('F@AHETPI')
ser2 <- pchange(us_core_level, 12)
ser <- pchange(wages, 12)
pp <- ShadeBars2(ser["2000-01-01/2012-01-01"],  ser2["2000-01-01/2012-01-01"], 
                 recession, c('Average Wage Growth', 'Core CPI'),  
                 ylab="Ann % Chg",main="U.S. Wage Growth And Core CPI", 
                 startdate='1990-01-01', legendpos=c(.4, .8),
                 legendhead='Annual Growth')
pp <- SetXAxis(pp, "2000-01-01", "2012-01-01")
#p2 <- p2 + geom_hline(yintercept=2.4,color=BondEconomicsBlue(),size=1)


rat <- wages / rebase(us_core_level, "2000-01-01")
p2 <- ShadeBars1(rat["2000-01-01/2012-01-01"],   
                 recession,   
                 ylab="$",main="U.S. Average Wages Deflated By Core CPI*", 
                 startdate='2000-01-01')
p2 <- SetXAxis(p2, "2000-01-01", "2012-01-01")


TwoPanelChart(pp, p2, "20210208_wage_core_cpi_ratio.png","*Base = Jan 2000. Source: BLS (via FRED).")




