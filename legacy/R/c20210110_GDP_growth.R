# (c) 2019 Brian Romanchuk
source('startup.R')

NGDP <- pfetch('F@GDP')
NGDP <- NGDP/1000
ser <- pchange(NGDP, 4)
recession <- pfetch('F@USREC')
pp <- ShadeBars1(ser, recession, 
              'Ann % Chg', main='U.S.: Nominal GDP Growth Rate',
              startdate = '1995-01-01')
pp <- SetXAxis(pp,"1995-01-01", 3)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)

realGDP <- pfetch('F@GDPc1')
realGDP <- realGDP["1995-01-01/"]
NGDP <- NGDP["1995-01-01/"]

n = coredata(NGDP)
r = coredata(realGDP)
M = length(n)

def[1] = n[1]/r[1]
for (i in 2:M)
{
  def[i] = def[i-1] *1.02
}
new_real = n/def
new_real_ser = xts(new_real, order.by=date(NGDP))

ser <- realGDP
ser2 <- new_real_ser
p2 <- ShadeBars2(ser, ser2, recession, 
                 'Tr $', main='U.S. Real GDP And Hypothetical',
                 legendhead='Real GDP', legendpos=c(.2, .7),
                 legend=c('Reported', '8% Inflation'),
                 startdate = '1995-01-01')
p2 <- SetXAxis(p2,"1995-01-01", 3)



TwoPanelChart(pp, p2,  "c20210110_GDP_growth.png","Shade indicates NBER recessions. Source: BEA (via FRED).")
