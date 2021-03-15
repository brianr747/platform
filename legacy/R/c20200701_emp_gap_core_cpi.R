source('startup.R')

u3 <- pfetch('F@UNRATE')
NAIRU <- pfetch('F@NROU')
recession <- pfetch('F@USREC')




UNGAP <- NAIRU - u3
ser <- UNGAP["1990-01-01/2020-01-01"]
pp <- ShadeBars1(ser,  recession,   
                 ylab="%",main="U.S. Employment Gap (NAIRU less Unemployment)", 
                 startdate='1990-01-01')
pp <- SetXAxis(pp, "1990-01-01", "2019-12-01")
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

us_core_level <-pfetch('F@CPILFESL')
wages <- pfetch('F@AHETPI')
ser <- pchange(us_core_level, 12)
p2 <- ShadeBars1(ser["1990-01-01/2020-01-01"],  recession,   
                 ylab="Ann % Chg",main="U.S. CPI Inflation Ex-Food And Energy", 
                 startdate='1990-01-01')
p2 <- SetXAxis(p2, "1990-01-01", "2019-12-01")
p2 <- p2 + geom_hline(yintercept=2.4,color=BondEconomicsBlue(),size=1)
p2 <- p2 + annotate("text",x=as.Date("2015-01-01"),y=2.8,size=2,label="Period Average (2.4%)")

TwoPanelChart(pp, p2, "c20200701_emp_gap_core_cpi.png","Source: BLS, CBO (via FRED).")




