# (c) 2019 Brian Romanchuk
source('startup.R')

M1 <- pfetch('F@M1')
M1m <- convertdm(M1)
GDP <- pfetch('F@GDP')
CPI <- pfetch('F@CPILFESL')
gdp_grow <- pchange(GDP, 4)
inf <- pchange(CPI, 12)
m_grow <- pchange (M1m, 12)

recession <- pfetch('F@USREC')
ser <- m_grow
ser2 <- gdp_grow
pp <- ShadeBars2(ser, ser2, recession, c('M1', 'Nominal GDP'),
              'Ann % Chg', main='M1 Growth And Nominal GDP',
              startdate = '1990-01-01', legendpos = c(.7, .8), 
              legendhead = 'Growth Rate:')
pp <- SetXAxis(pp,"1990-01-01", 5)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)


ser2 <- inf
p2 <- ShadeBars2(ser, ser2, recession, c('M1', 'Core CPI Inflation'),
                 'Ann % Chg', main='M1 Growth And Core Inflation',
                 startdate = '1990-01-01', legendpos = c(.7, .8), 
                 legendhead = 'Growth Rate:')
p2 <- SetXAxis(p2,"1990-01-01", 5)
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)

TwoPanelChart(pp, p2, "c20200812_money_fail.png","National sources, via FRED.")
