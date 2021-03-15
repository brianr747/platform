

# (c) 2020 Brian Romanchuk
source('startup.R')

gold <- pfetch('D@BOE/4048/XUDLGPD')
#gold <- pfetch('F@GOLDPMGBD228NLBM')
ser <- gold
recession <- pfetch('F@USREC')



pp <- ShadeBars1(ser["1980-01-01/2000-06-01"],  recession,   
                 ylab="$/oz.",main="Dollar Price Of Gold: The Ugly Years", 
                 startdate='1980-01-01')
pp <- SetXAxis(pp, "1980-01-01", "2000-06-01")

us_headline_level <- pfetch('F@CPIAUCSL')
rat <- convertdm(gold) / rebase(us_headline_level, "1980-01-01")
p2 <- ShadeBars1(rat["1980-01-01/2000-06-01"],  recession,   
                 ylab="$/oz.",main="Real Price Of Gold*: Deflated By Headline CPI*", 
                 startdate='1980-01-01')
p2 <- SetXAxis(p2, "1980-01-01", "2000-06-01")

TwoPanelChart(pp, p2, "cc20210215_gold_horror_show.png","*Jan 1980 dollars. Source: BoE via DB.nomics.")


