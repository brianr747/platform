

# (c) 2019 Brian Romanchuk
source('startup.R')

us_core_level <-pfetch('F@CPILFESL')
cpi <- pfetch('F@CPIAUCSL')
inf <- pchange(cpi,12)
core_inf <- pchange(us_core_level, 12)


ser <- inf
pp <- Plot2Ser(ser, core_inf, c('Headline', "Core"),
                 ylab="Ann % Chg",main="U.S. CPI Inflation", 
                 startdate='2010-01-01', legendpos=c(.4,.8),
               legendhead = 'Annual Rate')
pp <- SetXAxis(pp, "2010-01-01", 1)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

OnePanelChart(pp, "c20200512_us_inf.png","Source: BLS (via FRED).")



