

# (c) 2020 Brian Romanchuk
source('startup.R')

gold <- pfetch('F@GOLDPMGBD228NLBM')
ser <- gold
recession <- pfetch('F@USREC')


p2 <- ShadeBars1(ser,  recession,   
                 ylab="$/oz.",main="Dollar Price Of Gold", 
                 startdate='1970-01-01')
p2 <- SetXAxis(p2, "1970-01-01", 5)

OnePanelChart(p2, "c2020729_gold.png","Source: ICE Benchmark, 3 PM fix (via FRED).")


