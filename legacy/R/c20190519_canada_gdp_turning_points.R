source('basefn2.R')
source('utils.R')
#source('specialcharts2.R')

gdp <- pfetch('D@OECD/QNA/CAN.B1_GE.VIXOBSA.Q')

ser <- pchange(gdp,4)
turning_indic <- pfetch('F@CANRECM')


pp <- ShadeBars1(ser["1990-0101/"], turning_indic["1990-01-01/"], 
              'Ann % Chg', main='Canadian Real GDP And OECD Leading Indicator Turning Points*')
pp <- SetXAxis(pp,"1990-01-01", 3)
pp <- pp + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
# p2 = p2 + geom_rect(data=rec_dates, aes(xmin=Start, xmax=End, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.4)
PlotFromLowLevel(pp,"c20190519_canada_turning_points.png","*Shade represents turning points. Source: OECD (via DB.nomics & FRED).")

recession = pfetch('U@CANADIAN_RECESSIONS')
p2 <- ShadeBars1(ser["1990-0101/"], recession["1990-01-01/"], 
              'Ann % Chg', main='Canadian Real GDP And Recessions*')
p2 <- SetXAxis(p2,"1990-01-01", 3)
p2 <- p2 + geom_hline(yintercept=0,color=BondEconomicsBlue(),size=1)
# p2 = p2 + geom_rect(data=rec_dates, aes(xmin=Start, xmax=End, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.4)
PlotFromLowLevel(p2,"c20190519_canada_recessions.png","*C.D. Howe Business Cycle Council. Source: OECD (via DB.nomics).")

UR <- pfetch('STATCAN@14100287|v2062815')
p3 <- ShadeBars1(UR["1990-0101/"], recession["1990-01-01/"], 
              'Ann % Chg', main='Canadian Unemploment Rate And Recessions*')
p3 <- SetXAxis(p3,"1990-01-01", 3)
PlotFromLowLevel(p3,"c20190519_canada_UR_recessions.png","*C.D. Howe Business Cycle Council. Source: Statscan.")

# Minimum over 12 previous months *including current month*. (This way we
# always >= 0.
URmin = rollapplyr(UR, 12, min)
UR_rise = UR - URmin
p4 <- ShadeBars1(UR_rise["1990-01-01/"], recession["1990-01-01/"], 
              'Ann % Chg', main='Canadian Rise In Unemployment Rate* And Recessions**')
p4 <- SetXAxis(p4,"1990-01-01", 3)
PlotFromLowLevel(p4,"c20190519_canada_UR_rise_recessions.png","*Rise versus min over past year. **C.D. Howe. Source: Statscan.")


# Show BoC Rate

target_rate = pfetch('STATCAN@10100139|v39079', database='TEXT')
p5 <- ShadeBars1(target_rate["1993-01-01/"], recession["1993-01-01/"], 
              'Ann % Chg', main='Canadian Target Rate And Recessions*')
p5 <- SetXAxis(p5,"1993-01-01", 3)
PlotFromLowLevel(p5,"c20190519_canada_policy_rate_recessions.png","*C.D. Howe. Source: Bank of Canada via Statscan.")

# UR Rise versus OECD
p6 <- ShadeBars1(UR_rise["1990-01-01/"], turning_indic["1990-01-01/"], 
              'Ann % Chg', main='Canadian Rise In Unemployment Rate* And OECD Turning Points**')
p6 <- SetXAxis(p6,"1990-01-01", 3)
PlotFromLowLevel(p6,"c20190519_canada_UR_rise_turning_point.png","*Rise versus min over past year. **OECD (via FRED). Source: Statscan.")

