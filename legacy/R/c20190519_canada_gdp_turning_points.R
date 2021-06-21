source('startup.R')


total_emp <- pfetch('STATCAN@14100355|v2057603')
construction <- pfetch('STATCAN@14100355|v2057608')
recession = pfetch('U@CANADIAN_RECESSIONS')
ser <- 100*(construction/total_emp)
p2 <- ShadeBars1(ser["1976-01-01/"], recession["1976-01-01/"], 
              '%', main='Canada: Construction As % Of Total Employment')

PlotFromLowLevel(p2,"c20210617_canada_construction_employment.png","Shade indicates recessions (C.D. Howe). Source: Statscan.")

