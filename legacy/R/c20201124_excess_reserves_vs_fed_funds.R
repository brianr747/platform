# (c) 2020 Brian Romanchuk
source('startup.R')


excess <- pfetch('F@EXCSRESNW')
total <- pfetch('F@RESBALNSW')

ser <- 100*(excess/total)

fed_funds <- pfetch('F@DFF')

fed_funds_m <- convertdm(fed_funds)
excess_m <- convertdm(ser)

rng = '1984-02-01/1995-01-01'
fed_funds_m <- fed_funds_m[rng]
excess_m <- excess_m[rng]

pp <- Scatter1(coredata(excess_m), coredata(fed_funds_m), xlab='Excess Reserves As % Of Total',
               ylab='Effective Fed Funds Rate (%)', main='Excess Reserves Versus Fed Funds: 1984-1995')

OnePanelChart(pp, "c20201124_excess_reserves_vs_fed_funds.png","Source: H.3, H.15 (via FRED).")