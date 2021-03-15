# (c) 2021 Brian Romanchuk
source('startup.R')
recession <- pfetch('F@USREC')

tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
tsy5 <- pfetch('F@DGS5')
tsy30 <- pfetch('F@DGS30')


slope510 <- 100*(tsy10-tsy5)
slope1030 <- 100*(tsy30-tsy10)

pp <- ShadeBars2(slope510, slope1030, recession, 
                 c('5-/10-year', '10-/30-year'), 'BPs.', 
                 main='U.S. Slope Comparison',
                 startdate='1999-01-01', legendhead='Slope')
pp <- SetXAxis(pp,"1999-01-01", 4)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)



slope_rate_5_10 <- slope510/(10-5)
slope_rate_10_30 <- slope1030/(30-10)
p2 <- ShadeBars2(slope_rate_5_10, slope_rate_10_30, recession, 
                 c('Between 5 and 10 years', 'Between 10 and 30 years'), 'BPs./Year', 
                 main='U.S. Slope Change Comparison',
                 startdate='1999-01-01', legendhead='Change In Slope Per Year')
p2 <- SetXAxis(p2,"1999-01-01", 4)
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp, p2, "c20210121_slope_compare_2.png","Shade indicates NBER recessions. Source: Fed H.15 (via FRED).")

