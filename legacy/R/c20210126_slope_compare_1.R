# (c) 2021 Brian Romanchuk
source('startup.R')
recession <- pfetch('F@USREC')

tsy2 <- pfetch('F@DGS2')
tsy10 <- pfetch('F@DGS10')
tsy5 <- pfetch('F@DGS5')

slope210 <- 100*(tsy10-tsy2)
slope510 <- 100*(tsy10-tsy5)
slope25 <- 100*(tsy5-tsy2)

pp <- ShadeBars2(slope25, slope510, recession, 
                 c('2-/5-year', '5-/10-year'), 'BPs.', 
                 main='U.S. Slope Comparison',
                 startdate='1999-01-01', legendhead='Slope')
pp <- SetXAxis(pp,"1999-01-01", 4)
pp <- pp + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


slope_rate_2_5 <- slope25/(5-2)
slope_rate_5_10 <- slope510/(10-5)
p2 <- ShadeBars2(slope_rate_2_5, slope_rate_5_10, recession, 
                 c('Between 2 and 5 Years', 'Between 5 and 10 years'), 'BPs./Year', 
                 main='U.S. Slope Change Comparison',
                 startdate='1999-01-01', legendhead='Change In Slope Per Year')
p2 <- SetXAxis(p2,"1999-01-01", 4)
p2 <- p2 + geom_hline(colour=BondEconomicsBlue(), yintercept=0)


TwoPanelChart(pp, p2, "c20210121_slope_compare_1.png","Shade indicates NBER recessions. Source: Fed H.15 (via FRED).")

