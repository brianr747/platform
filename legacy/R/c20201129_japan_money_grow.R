source('startup.R')

japan_m_grow <- pfetch('D@IMF/MFS/M.JP.FASMB_PC_CP_A_PT')

ser <- japan_m_grow
pp <- Plot1Ser(ser, 
                 'Ann. % Chg', main='Japan: Annual Growth Of Monetary Base',
                 startdate = '1993-01-01')
pp <- SetXAxis(pp,"2003-01-01",3)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

OnePanelChart(pp, "c20201129_japan_money.png","Source: IMF (via DB.nomics).")
