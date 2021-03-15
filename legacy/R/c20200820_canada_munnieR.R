
source('startup.R')



m_base <- pfetch('STATCAN@10100116|v37146')
m2p <- pfetch('STATCAN@10100116|v41552798')


p1 <- ShadeBars1(m_base/1000, recession, 'Billion $', main='Canadian Monetary Base',
                 startdate='2007-01-01')
p1 <- SetXAxis(p1, "2007-01-01", 1)

pp <- ShadeBars1(pchange(m2p, 12), recession, 'Ann % Chg', main='Canada: M2+ Growth Rate',
                 startdate='2007-01-01')
pp <- SetXAxis(pp, "2007-01-01", 1)


TwoPanelChart(p1, pp, "c20200820_canada_munnie.png","Shade represents recession (C.D. Howe). Source: BoC.")
