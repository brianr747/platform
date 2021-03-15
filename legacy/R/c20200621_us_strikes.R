source('startup.R')

# The BLS data is in a ^$%&-ed up Excel spreadsheet; manually fixed
# and put into a CSV.
# Source: https://www.bls.gov/wsp/
foo <- read.csv('us_strike_hours.txt', sep='\t')

us_strikes <- xts(foo$num_days, 
                  as.Date(as.character(foo$Year), format='%Y'))

ser <- us_strikes/1000
p2 <- PlotLowLevel1(ser, 'Millions', 'United States: Annual Hours Lost In Work Stoppages')
p2 <- SetXAxis(p2, "1947-01-01", 5)
p2 <- p2 + geom_hline(yintercept=6,color=BondEconomicsBlue(),size=1)
p2 <- p2 + geom_vline(colour=BondEconomicsBlue(), xintercept=as.numeric(as.Date("1990-01-01")))
p2 <- p2 + annotate("text",x=as.Date("1970-01-01"),y=3.5,size=2,label="Floor")
p2 <- p2 + annotate("text",x=as.Date("2010-01-01"),y=9,size=2,label="Ceiling")



OnePanelChart(p2, "c20200621_us_strikes.png","Source: BLS Website.")




