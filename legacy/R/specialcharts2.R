source("basefn2.R")
x <- parent.frame(2)$ofile
print(x)
IMFLowLevel <- function(IID,legend="",ylab="",main="",legendpos=c(.8,.8),hasmarker=T,transform=""){
  if (legend=="") {
    legend=IID
  }
  res <- DBLoadIMF(IID,transform)
  pp <- PlotLowLevel2(res$series,res$projection,
                      c(legend,"Estimates"),ylab,main,
                      legendpos,hasmarker)
  d1 <- time(res$series)
  d2 <- time(res$projection)
  t1 <- d1[1]
  t2 <- d2[length(d2)]
  pp <- pp + coord_cartesian(xlim=c(t1,t2))
  return(list(pp=pp,footer="Source: IMF World Economic Outlook."))
  
}

IMFPlot1 <- function(IID,legend="",ylab="",main="",fname="tmp.png",legendpos=c(.8,.8),hasmarker=T,transform=""){
  x = IMFLowLevel(IID,legend,ylab,main,legendpos,hasmarker,transform)
  PlotFromLowLevel(x$pp,fname,x$footer)
}
MyNBERBars <- function(ser,ylab="",main="",show_watermark=T,has_marker=F){
  # Based on http://jeffreybreen.wordpress.com/2011/08/15/recession-bars/
  recessions.df = read.table(textConnection(
    "Peak, Trough
    1857-06-01, 1858-12-01
    1860-10-01, 1861-06-01
    1865-04-01, 1867-12-01
    1869-06-01, 1870-12-01
    1873-10-01, 1879-03-01
    1882-03-01, 1885-05-01
    1887-03-01, 1888-04-01
    1890-07-01, 1891-05-01
    1893-01-01, 1894-06-01
    1895-12-01, 1897-06-01
    1899-06-01, 1900-12-01
    1902-09-01, 1904-08-01
    1907-05-01, 1908-06-01
    1910-01-01, 1912-01-01
    1913-01-01, 1914-12-01
    1918-08-01, 1919-03-01
    1920-01-01, 1921-07-01
    1923-05-01, 1924-07-01
    1926-10-01, 1927-11-01
    1929-08-01, 1933-03-01
    1937-05-01, 1938-06-01
    1945-02-01, 1945-10-01
    1948-11-01, 1949-10-01
    1953-07-01, 1954-05-01
    1957-08-01, 1958-04-01
    1960-04-01, 1961-02-01
    1969-12-01, 1970-11-01
    1973-11-01, 1975-03-01
    1980-01-01, 1980-07-01
    1981-07-01, 1982-11-01
    1990-07-01, 1991-03-01
    2001-03-01, 2001-11-01
    2007-12-01, 2009-06-01"), sep=',',
    colClasses=c('Date', 'Date'), header=TRUE)
  datez = time(ser)
  series.df = data.frame(date=datez,val=coredata(ser))
  names(series.df) <- c("date","val")  # Why is this necessary?
  pp <- ggplot(series.df) + geom_line(aes(x=date,y=val))
  if (has_marker){
    pp <- pp + geom_point(aes(x=date,y=val))
  }
  recessions.trim = subset(recessions.df, Peak >= min(datez)) 
  print(recessions.trim)
  pp = pp + geom_rect(data=recessions.trim, aes(xmin=Peak, xmax=Trough, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.4)
  if (show_watermark){
    pp <- AddWatermark(pp,x=datez[1],y=-Inf)
  }
  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  
  return(pp)
}


MyNBERBars2 <- function(ser1,ser2,legend=c("series1","series2"),ylab="",main="",legendpos=c(.2,.8),show_watermark=T){
  # Based on http://jeffreybreen.wordpress.com/2011/08/15/recession-bars/
  recessions.df = read.table(textConnection(
    "Peak, Trough
    1857-06-01, 1858-12-01
    1860-10-01, 1861-06-01
    1865-04-01, 1867-12-01
    1869-06-01, 1870-12-01
    1873-10-01, 1879-03-01
    1882-03-01, 1885-05-01
    1887-03-01, 1888-04-01
    1890-07-01, 1891-05-01
    1893-01-01, 1894-06-01
    1895-12-01, 1897-06-01
    1899-06-01, 1900-12-01
    1902-09-01, 1904-08-01
    1907-05-01, 1908-06-01
    1910-01-01, 1912-01-01
    1913-01-01, 1914-12-01
    1918-08-01, 1919-03-01
    1920-01-01, 1921-07-01
    1923-05-01, 1924-07-01
    1926-10-01, 1927-11-01
    1929-08-01, 1933-03-01
    1937-05-01, 1938-06-01
    1945-02-01, 1945-10-01
    1948-11-01, 1949-10-01
    1953-07-01, 1954-05-01
    1957-08-01, 1958-04-01
    1960-04-01, 1961-02-01
    1969-12-01, 1970-11-01
    1973-11-01, 1975-03-01
    1980-01-01, 1980-07-01
    1981-07-01, 1982-11-01
    1990-07-01, 1991-03-01
    2001-03-01, 2001-11-01
    2007-12-01, 2009-06-01"), sep=',',
    colClasses=c('Date', 'Date'), header=TRUE)
  
  datez <- c(time(ser1),time(ser2))
  valz <- c(coredata(ser1),coredata(ser2))
  colors <-factor(c(
    rep("s1",length(time(ser1))),
    rep("s2",length(time(ser2)))
  ))
  
  levels(colors) = legend
  series.df <- data.frame(datez,valz,colors)
  
  names(series.df) <- c("date","val","colors")  # Why is this necessary?
  pp <- ggplot(series.df,aes(x=date,y=val,colour=colors)) + geom_line()
  recessions.trim = subset(recessions.df, Peak >= min(datez)) 
  print(recessions.trim)
  
  if (show_watermark){
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=datez[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=.8)
  }
  pp <- pp + scale_colour_manual("",values=c("black","red"))
  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  #pp = pp + geom_rect(data=recessions.trim, aes(xmin=Peak, xmax=Trough, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.4)
  return(pp)
}

MyNBERBars_bad <- function(pp,ser){
  # Based on http://jeffreybreen.wordpress.com/2011/08/15/recession-bars/
  recessions.df = read.table(textConnection(
    "Peak, Trough
1857-06-01, 1858-12-01
    1860-10-01, 1861-06-01
    1865-04-01, 1867-12-01
    1869-06-01, 1870-12-01
    1873-10-01, 1879-03-01
    1882-03-01, 1885-05-01
    1887-03-01, 1888-04-01
    1890-07-01, 1891-05-01
    1893-01-01, 1894-06-01
    1895-12-01, 1897-06-01
    1899-06-01, 1900-12-01
    1902-09-01, 1904-08-01
    1907-05-01, 1908-06-01
    1910-01-01, 1912-01-01
    1913-01-01, 1914-12-01
    1918-08-01, 1919-03-01
    1920-01-01, 1921-07-01
    1923-05-01, 1924-07-01
    1926-10-01, 1927-11-01
    1929-08-01, 1933-03-01
    1937-05-01, 1938-06-01
    1945-02-01, 1945-10-01
    1948-11-01, 1949-10-01
    1953-07-01, 1954-05-01
    1957-08-01, 1958-04-01
    1960-04-01, 1961-02-01
    1969-12-01, 1970-11-01
    1973-11-01, 1975-03-01
    1980-01-01, 1980-07-01
    1981-07-01, 1982-11-01
    1990-07-01, 1991-03-01
    2001-03-01, 2001-11-01
    2007-12-01, 2009-06-01"), sep=',',
colClasses=c('Date', 'Date'), header=TRUE)
  datez = time(ser)
  print(datez)
  #series.df = data.frame(date=datez,val=coredata(ser))
  #pp <- ggplot(series.df) + geom_line(aes(x=date,y=val))
  recessions.trim = subset(recessions.df, Peak >= min(datez)) 
  print(recessions.trim)
  pp = pp + geom_rect(data=recessions.trim, aes(xmin=Peak, xmax=Trough, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.2)
  return(pp)
}


PlotLowLevel1_Raw <- function(t,x,ylab="",main="",seekingAlpha=F,xlab="",hasmarker=F){
  dates <- t
  valz <- x
  xx <- data.frame(dates,valz)
  names(xx) <- c("dates","valz")
  pp <- ggplot(xx,aes(x=dates,y=valz)) + geom_line()
  if (!seekingAlpha){
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
  }
  pp <- pp + geom_line()
  if (hasmarker){
    pp <- pp + geom_point(size=2.5)
  }
  pp <- pp + ylab(ylab)
  if (xlab=="") {
    pp <- pp + theme(axis.title.x = element_blank())
  }else{
    pp <- pp + xlab(xlab)
  }
  pp <- pp + ggtitle(main)
  return(pp)
}

PlotLowLevel2_Raw <- function(t1,x1,t2,x2,legend=c("series1","series2"),
                          ylab="",main="",legendpos=c(.8,.8),
                          hasmarker=F,xlab=""){
  dates <- c(t1,t2)
  valz <- c(x1,x2)
  colors <-factor(c(
    rep("s1",length(t1)),
    rep("s2",length(t2))
  ))
  
  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  if(hasmarker){
    pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line() + geom_point(size=2.5)
  }
  else{
    pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line()
  }
  pp <- pp + scale_colour_manual("",values=c("black","red"))
  pp <- pp + ylab(ylab)
  if (xlab=="") {
    pp <- pp + theme(axis.title.x = element_blank())
  }else{
    pp <- pp + xlab(xlab)
  }
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}

PlotLowLevel3_Raw <- function(t1,x1,t2,x2,t3,x3,legend=c("series1","series2","series3"),
                              ylab="",main="",legendpos=c(.8,.8),
                              hasmarker=F,xlab="",legendhead=""){
  dates <- c(t1,t2,t3)
  valz <- c(x1,x2,x3)
  colors <-factor(c(
    rep("s1",length(t1)),
    rep("s2",length(t2)),
    rep("s3",length(t2))
  ))
  
  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  if(hasmarker){
    pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line() + geom_point(size=2.5)
  }
  else{
    pp <- ggplot(xx,aes(x=dates,y=valz,linetype=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line()
  }
  pp <- pp + scale_linetype_manual(legendhead ,values=c(1,2,3))
  #pp <- pp + scale_colours_manual(legendhead,values=c("black","red","green"))
  pp <- pp + ylab(ylab)
  if (xlab=="") {
    pp <- pp + theme(axis.title.x = element_blank())
  }else{
    pp <- pp + xlab(xlab)
  }  
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}

SeasonalChart <- function(ser,
                              ylab="",main="",legendpos=c(.8,.8),
                              hasmarker=T){
  tt <- time(ser)
  Year = format(tt,"%Y")
  Month = as.numeric(format(tt,"%m"))

  valz <- coredata(ser)
#   colors <-factor(c(
#     rep("s1",length(t1)),
#     rep("s2",length(t2))
#   ))
  
#  levels(colors) = legend
  xx <- data.frame(valz,Year,Month)
  if(hasmarker){
    pp <- ggplot(xx,aes(x=Month,y=valz,colour=Year,shape=Year))
    pp <- pp + annotate("text",x=1,y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line() + geom_point(size=2.5)
  }
  else{
    pp <- ggplot(xx,aes(x=Month,y=valz,colour=Year))
    pp <- pp + annotate("text",1,y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line()
  }
  #pp <- pp + scale_colour_manual("",values=c("black","red"))
  pp <- pp + scale_x_continuous(breaks=1:12)
  pp <- pp + ylab(ylab)
  #pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}