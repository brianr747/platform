source('basefn2.R', encoding='UTF-8')

# NOTE: The series need to be loaded from the database; the directly fetched data uses a date
# format that blows up R.
ser <- pfetch("ABSXLS@A2325846C")

inf <- pchange(ser, 4)
p <- PlotLowLevel1(inf["1975-01-01/"],"%","Australian Annual CPI Inflation")
p <- SetXAxis(p,"1981-01-01", 2)

ur_sa =pfetch("ABSXLS@A84423050A")

p2 <- PlotLowLevel1(ur_sa, '%', 'Australian Unemployment Rate (S.A.)')
p2 <- SetXAxis(p2,"1981-01-01", 2)

Plot2FromLowLevel(p, p2, "c20190507_australia_inflation.png","Source: ABS")

# Do a scatter. inf is quarterly, ur_sa is monthly.
# Use convertdq() on both, so they both have quarterly indexes
ur_sa_q <- convertdq(ur_sa["1978-01-01/2018-12-01"])
inf_q <- convertdq(inf["1978-01-01/2018-12-01"])
both <- merge(ur_sa_q, inf_q)


df = data.frame(both$ur_sa_q, both$inf_q)
names(df) = c("x","y") 

foottext <- "Source: ABS."

pp <- ggplot(df,aes(x=x,y=y))
# The "x" placement needs to be manually set..
pp <- pp + annotate("text",x=4,y=0.3,label="BondEconomics.com",
                    color="white",vjust=-.3,hjust=-.05,size=9,alpha=.8)
pp <- pp + geom_point(shape=1)
print(pp)
pp <- pp + stat_smooth(method=lm,size=1.5,colour="#1177FF")
pp <- pp + ylab("Annual CPI Inflation (%)")
pp <- pp + xlab("Unemployment Rate %")
pp <- pp + ggtitle("Australia: Unemployment Rate Versus CPI Inflation (1978-2018)")
print(pp)
PlotFromLowLevel(pp,"c20190507_australia_ur_inf_scatter.png",foottext)


# Do underemployment

underemployment <- pfetch('ABSXLS@A85255724F')
pp <- PlotLowLevel1(underemployment, '%', 'Australian Underemployment Rate (S.A.)')
pp <- SetXAxis(pp,"1981-01-01", 2)
PlotFromLowLevel(pp, "c20190507_australia_underemployment.png", "Source: ABS")

# Yeah, I needed to wrap scatter plots...
under_q <- convertdq(underemployment["1978-01-01/2018-12-01"])

both <- merge(under_q, inf_q)


df = data.frame(both$under_q, both$inf_q)
names(df) = c("x","y") 

foottext <- "Source: ABS."

pp <- ggplot(df,aes(x=x,y=y))
# The "x" placement needs to be manually set..
pp <- pp + annotate("text",x=2,y=0.3,label="BondEconomics.com",
                    color="white",vjust=-.3,hjust=-.05,size=9,alpha=.8)
pp <- pp + geom_point(shape=1)
print(pp)
pp <- pp + stat_smooth(method=lm,size=1.5,colour="#1177FF")
pp <- pp + ylab("Annual CPI Inflation (%)")
pp <- pp + xlab("Underemployment Rate %")
pp <- pp + ggtitle("Australia: Underemployment Rate Versus CPI Inflation (1978-2018)")
print(pp)
PlotFromLowLevel(pp,"c20190507_australia_under_inf_scatter.png",foottext)

