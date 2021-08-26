# (c) 2019 Brian Romanchuk
source('startup.R')


recession <- pfetch('F@USREC')
cpi_core <- pfetch('F@CPILFESL')
cpi_headline <- pfetch('F@CPIAUCSL')
cleveland <- pfetch('MEDCPIM094SFRBCLE')

ser2 <- pchange(cpi_headline, 12)
ser <- MA(pchange(cleveland,12), 3)
p1 <- ShadeBars2(ser["1990-01-01/"], ser2["1990-01-01/"], recession, c('Median Fed (3 mo. M.A.)', 'All Items'),  
                 ylab="Ann % Chg",main="U.S.: Median CPI Versus Headline", legendhead='CPI',
                 legendpos=c(.2,.7), startdate='1990-01-01')
p1 <- SetXAxis(p1, "1990-01-01", "2024-01-01")



OnePanelChart(p1,"c20190713_cleveland_fed.png","Source: BLS, Cleveland Fed (via FRED).")
