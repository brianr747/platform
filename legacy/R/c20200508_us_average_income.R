# (c) 2019 Brian Romanchuk
source('startup.R')

wages <- pfetch('F@AHETPI')
ser <- pchange(wages, 12)
pp <- Plot1Ser(ser,  
              'Ann % Chg', main='U.S. Wages: All Private Non-Supervisory',
              startdate = '1980-01-01')
pp <- SetXAxis(pp,"1980-01-01", 3)
#pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

OnePanelChart(pp, "c20200508_us_average_income.png","Source: BLS (via FRED).")
