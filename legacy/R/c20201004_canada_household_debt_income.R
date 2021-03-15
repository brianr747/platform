
source('startup.R')


hh_debt_income <- pfetch('STATCAN@38100235|v62698063')
#gcan5 <- pfetch('STATCAN@10100145|v80691324')
recession <- pfetch('U@CANADIAN_RECESSIONS')

#rng <- '1990-01-01/1995-01-01'
p1 <- ShadeBars1(hh_debt_income, recession, '%', main='Canada: Household Debt to Disposable Income',
                 startdate='1990-01-01')
p1 <- SetXAxis(p1, "1990-01-01", 3)



OnePanelChart(p1, "c20201004_canada_household_debt_income.png","Shade represents recessions (C.D. Howe). Source: Statscan.")
