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
pp <- pp + geom_hline(colour="red", yintercept=5)
pp <- pp + annotate("text",x=as.Date("2016-01-01"),y=6,size=2,label="Growth Target")


ser <- NGDP
targ <- 0 * NGDP["2002-01-01/"]
targ["2002-01-01", 1] <- NGDP["2002-01-01", 1]



L <- length(targ)
for (pos in 2:L){
  targ[pos,1] <- 1.0125 * targ[(pos-1),1]
}
ser2 <- targ

p2 <- ShadeBars2(ser, ser2, recession, 
                 'Tr $', main='U.S.: Nominal GDP And Level Target',
                 legendhead='Level of GDP', legendpos=c(.2, .7),
                 legend=c('Actual', 'Target (Base = 2002 Q1)'),
                 startdate = '1995-01-01')
p2 <- SetXAxis(p2,"1995-01-01", 3)


TwoPanelChart(pp,p2, "c20200216_GDP_rate_level.png","Shade indicates NBER recessions. Source: BEA (via FRED).")

ser <- 100*(NGDP-targ)/NGDP
p3 <- ShadeBars1(ser, recession, "% of GDP", "Nominal GDP Deviation From Level Target", 
                 startdate="2002-01-01")
p3 <- SetXAxis(p3, "2002-01-01", "2014-01-01")
p3 <- p3 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)
OnePanelChart(p3,  "c20200216_GDP_rate_level-2.png","Shade indicates NBER recessions. Source: BEA (via FRED).")
