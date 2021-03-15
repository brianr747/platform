# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('U@CANADIAN_RECESSIONS')
ser <- pfetch('STATCAN@38100238|v1038036699')
pp <- ShadeBars1(ser, recession,  
                 ylab="%",main="Canada: Household Debt To Disposable Income", 
                 startdate='1990-01-01')
pp <- SetXAxis(pp, "1990-01-01", 4)

OnePanelChart(pp, "c20190908_canada_household_debt.png","Shaded bars indicate recessions (C.D. Howe). Source: Statscan.")

