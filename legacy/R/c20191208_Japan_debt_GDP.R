# (c) 2019 Brian Romanchuk
source('startup.R')

net <- pfetch('D@IMF/GFSMAB/A.JP.S13.XDC_R_B1GQ.G63N_FD4')

ser <- net
pp <- Plot1Ser(ser,
                 '% of GDP', main='Japan General Government Net Debt',
                 startdate = '1999-01-01')

pp <- pp + geom_hline(yintercept=63.68,color=BondEconomicsBlue(),size=1)
pp <- pp + geom_hline(yintercept=128.9,color=BondEconomicsBlue(),size=1)
pp <- pp + geom_vline(colour="red", xintercept = as.numeric(as.Date("2010-01-01")))
pp <- SetXAxis(pp, "1999-01-01", 2)


ser <- pfetch('D@IMF/IFS/M.JP.FIGB_PA')
p2 <- Plot1Ser(ser,
               '%', main='Japan: Government Bond Yield',
               startdate = '1999-01-01')
p2 <- SetXAxis(p2, "1999-01-01", 2)
p2 <- p2 + geom_vline(colour="red", xintercept = as.numeric(as.Date("2010-01-01")))


TwoPanelChart(pp, p2, "c20191208_Japan_net_debt.png","Source: IMF (via DBnomics).")

