

# (c) 2019 Brian Romanchuk
source('startup.R')


tsy = pfetch("F@DGS10")

fed = pfetch("F@DFF")
tsy <- convertdm(tsy)
fed <- convertdm(fed)
mod <- lag(MA(fed,120),1)



ser <- tsy
ser2 <- mod
pp <- Plot2Ser(ser, ser2, c('Actual', 'Simplest Bond Model'),
                 ylab="%",main="World's Simplest Bond Model", 
                 startdate='1985-01-01', legendhead = 'U.S. 10-Year Treasury',
               legendpos =c(.7, .7))
pp <- SetXAxis(pp, '1985-01-01', 5)
OnePanelChart(pp, "c20200520_simplest_bond_model.png","Source: Fed H.15 (via FRED), author calculations.")



