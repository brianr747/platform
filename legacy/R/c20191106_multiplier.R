source('startup.R')



G <- pfetch_real('SFC@SIM|GOV__DEM_GOOD', 'TMP')
G <- G[0:20,]
pp <- PlotXYReal(G$series_dates, G$series_values, main='Government Spending', has_marker = TRUE)


GDP <- pfetch_real('SFC@SIM|BUS__SUP_GOOD', 'TMP')
GDP <- GDP[0:20,]
p2 <- PlotXYReal(GDP$series_dates, GDP$series_values, main='Domestic Production (GDP)', has_marker = TRUE)




TwoPanelChart(pp,p2, "c20191106_multiplier.png","Simulation using textbook Model SIM parameters.")
