# (c) 2019 Brian Romanchuk
source('startup.R')

recession <- pfetch('U@CANADIAN_RECESSIONS')
ser <- pfetch('STATCAN@11100065|v1001696813')
pp <- ShadeBars1(ser, recession,  
                 ylab="%",main="Canada: Household Debt Service Ratio (Interest and Principal)", 
                 startdate='1990-01-01')
pp <- SetXAxis(pp, "1990-01-01", 4)

OnePanelChart(pp, "c20190908_canada_household_deb_service.png","Shaded bars indicate recessions (C.D. Howe). Source: Statscan.")

