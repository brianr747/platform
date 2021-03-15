

# (c) 2019 Brian Romanchuk
source('startup.R')


oil_prod <- pfetch('D@EIA/INTL/55-1-USA-TBPD.M')

ser <- oil_prod/1000
pp <- Plot1Ser(ser,  
                 ylab="Mn Bbl/Day",main="U.S. Crude Liquids Productions", 
                 startdate='1995-01-01')
pp <- SetXAxis(pp, "1995-01-01", 3)

OnePanelChart(pp, "c20200330_oil_production.png","Source: EIA (via DB.nomics).")



