

# (c) 2019 Brian Romanchuk
source('startup.R')

meat_cpi <- pfetch('F@CUSR0000SAF112')

ser <- meat_cpi
pp <- Plot1Ser(ser,  
                 ylab="",main="U.S. CPI Component: Meat, Poultry, Fish, And Eggs", 
                 startdate='2015-01-01')
pp <- SetXAxis(pp, "2015-01-01", "2020-09-01")

OnePanelChart(pp, "c20200430_us_meat_cpi.png","Source: BLS (via FRED).")



