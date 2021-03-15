source('startup.R')

u3 <- pfetch('F@UNRATE')
NAIRU <- pfetch('F@NROU')
recession <- pfetch('F@USREC')


ser <- u3["1990-01-01/2020-01-01"]
ser2 <- NAIRU["1990-01-01/2020-01-01"]

pp <- ShadeBars2(ser,  ser2, recession, c('Unemployment Rate', 'NAIRU (long term)'),  
                 ylab="%",main="U.S. Unemployment And CBO NAIRU", 
                 startdate='1990-01-01', legendhead='U.S.', legendpos=c(.3,.7))
pp <- SetXAxis(pp, "1990-01-01", "2019-12-01")

UNGAP <- NAIRU - u3
ser <- UNGAP["1990-01-01/2020-01-01"]
p2 <- ShadeBars1(ser,  recession,   
                 ylab="%",main="U.S. Employment Gap (NAIRU less Unemployment)", 
                 startdate='1990-01-01')
p2 <- SetXAxis(p2, "1990-01-01", "2019-12-01")
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

TwoPanelChart(pp, p2, "c20200701_NAIRU_U3.png","Source: BLS, CBO (via FRED).")




