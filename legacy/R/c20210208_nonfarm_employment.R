source('startup.R')


recession <- pfetch('F@USREC')






nonfarm <- pfetch('F@PAYEMS')
ser <- nonfarm/1000


pp <- ShadeBars1(ser["2000-01-01/2012-01-01"],   
                 recession,   
                 ylab="Millions",main="U.S. Total Nonfarm Employment", 
                 startdate='2000-01-01')
pp <- SetXAxis(pp, "2000-01-01", "2012-01-01")


OnePanelChart(p2, "20210208_nonfarm_employment.png","Source: BLS (via FRED).")




