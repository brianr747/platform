

# (c) 2019 Brian Romanchuk
source('startup.R')
tsy <- pfetch("F@LTGOVTBD")
tsy <- tsy["1935-01-01/1952-01-01"]

d = as.Date(c("1941-12-01","1951-03-01"))
accord = xts(c(2.5,2.5),order.by=d)

pp = Plot2Ser(tsy,accord,c("Long-Term Treasury Bond Yield","Yield Cap"),"%",
             "Long-Term U.S. Treasury Yield Capped Pre-Treasury/Fed Accord",
             legendpos=c(.5,.8))



pp <- SetXAxis(pp, '1935-01-01', '1952-01-01')
OnePanelChart(pp, "c20200522_treasury_accord.png","Source: Fed H.15 (via FRED).")



