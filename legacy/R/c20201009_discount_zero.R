
source('startup.R')

t = (0:100)/10
shock = (0:80)/(80*100)
zr = c(rep(0, 20), shock)
zr = zr + .05

#zr <- c(.05,.05,.05,.05 +(1:8)/800) 


df = 1/(1+zr)^t

p1 <- PlotXYReal(t, 100*zr, '%', main='Zero Rate')

p2 <- PlotXYReal(t, df, '', main='Discount Factor')


TwoPanelChart(p1, p2, "c20201010_discount_zero.png"," ")
