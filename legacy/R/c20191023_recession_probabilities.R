# (c) 2019 Brian Romanchuk
source('startup.R')

ser <- pfetch("F@RECPROUSM156N")
recession <- pfetch('F@USREC')

p2 <- ShadeBars1(ser, recession, "%","U.S. Recession Probability (Smoothed)",
                 startdate='1968-01-01')
p2 <- SetXAxis(p2, '1968-01-01', '2019-08-01')
OnePanelChart(p2,"c20191023_probabilities.png","Source: Piger & Chauvet, downloaded via FRED.")
