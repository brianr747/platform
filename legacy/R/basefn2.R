# Note: This code is not particularly good; it works,
# but not particularly stable nor clean.
#
# Cleaned up versions will migrate to a "R" subdirectory.


require("extrafont")
# extrafont::loadfonts(device="win")
require("RODBC")
require("xts")
require("ggplot2")
require("grid")
require("quantmod")
require("latticeExtra")
require("gridExtra")
require("lubridate")

# If updating, need to run 
# font_import() 
# Once (after importing extrafont)
require("TTR")


source('platformstartup.R')


BondEconomicsBlue <- function() {return("#4D469C")}

# This function assumes that the TEXT database has been 
# set to point to a "text_database" subdirectory.
FetchText <- function(ticker){
  # Need to make a valid file name.
  # gsub('\\.', '_', x) replaces "." with "_"
  # make.names() will get rid of invalid characters.
  # (Would run into issues if the ticker was a reserved
  # word, but that shouldn't happen.)
  file_base <- gsub('\\.', '_', make.names(ticker))
  file_name = paste("text_database\\", file_base, '.txt',
                    sep = '')
  df = read.csv(file_name, sep='\t')
  x = xts(df[,2], order.by = as.Date(df[,1]))
  return(x)
}


GetConn <- function() {
	conn <- odbcConnect("EconDB")
	return(conn)
} 

GetRes <- function() {return(133.333)}
GetImgDir <- function() {return (".\\images\\")}
GetFootText <- function() {return("(C) 2019 B. Romanchuk")}

DBLoad <- function(IID){
conn <- GetConn()
k <- sqlQuery(conn,sprintf("SELECT h.ddate as ddate,h.val as val FROM main_hist as h, main_prop as p WHERE p.sercode=h.sercode AND p.IID = '%s' ORDER BY ddate ASC",IID))
close(conn)
if (length(k$ddate) ==0){
  stop(sprintf("IID does not exist: %s",IID))
}
ser <- xts(k$val,order.by=k$ddate)
return(ser)

}

DBLoadPropRaw <- function(IID,prop="*"){
  conn <- GetConn()
  k <- sqlQuery(conn,sprintf("SELECT %s FROM main_prop WHERE IID = '%s'",prop,IID))
  close(conn)
  return(k)
}

DBLoadIMF <- function(IID,transform=""){
  conn <- GetConn()
  k <- sqlQuery(conn,sprintf("SELECT h.ddate as ddate,h.val as val FROM main_hist as h, main_prop as p WHERE p.sercode=h.sercode AND p.IID = '%s' ORDER BY ddate ASC",IID))
  close(conn)
  estdate_raw <- DBLoadPropRaw(IID,"ESTIMATE_AFTER")
  estdate <- estdate_raw$ESTIMATE_AFTER
  ser <- xts(k$val,order.by=k$ddate)
  if (transform=="pchange"){
    ser <- pchange(ser,1)
  }
  proj <- ser[sprintf("%i-12-31/",estdate)]
  cut <- ser[sprintf("/%i-12-01",estdate)]
  out = list(alldata=ser,series=cut,projection=proj)
}

# DBLoadFred <- function(ident) {
# conn <- GetConn()
# k <- sqlQuery(conn,sprintf("SELECT ddate,val FROM tempfred WHERE ident = '%s' ORDER BY ddate",ident))
# close(conn)
# ser = xts(k$val,order.by=k$ddate)
# return(ser)
# }
DBLoadFred <- function(ident) {
IID <- paste("FR",ident) # sticks " " in automatically...
ser <- DBLoad(IID)
return(ser)
}

DBLoadFoF <- function(ident) {
conn <- GetConn()
k <- sqlQuery(conn,sprintf("SELECT ddate,val FROM ext_FoF_simple WHERE ccode = '%s' ORDER BY ddate",ident))

close(conn)
ser = xts(k$val,order.by=k$ddate)
return(ser)
}

DBLoadGallup <- function(ident) {
conn <- GetConn()
k <- sqlQuery(conn,sprintf("SELECT ddate,%s AS val FROM ext_gallup_unemp WHERE %s IS NOT NULL ORDER BY ddate",ident,ident))
close(conn)
ser = xts(k$val,order.by=k$ddate)
return(ser)
}

###########################################################
mmonth <- function(x) format(x,'%Y %m')

convertdm <- function(x) {
x <- aggregate(x,by=mmonth,FUN=mean)
t <- as.Date(paste(gsub(" ","-",time(x)),"-01",sep=""))
valz <- coredata(x)
return(xts(valz,order.by=t))
}

convertdq <- function(x){
  x <-aggregate(x,by=as.yearqtr,FUN=mean)
  return(x)
}
as.year <- function(x) floor(as.numeric(as.yearmon(x)))
convertdy <- function(x){
  x <-aggregate(x,by=as.year,FUN=mean)
  return(x)
}

rebase <- function(ser,ddate){
  k = as.numeric(ser[ddate])
  ser = ser/k
  return(ser)
}

forwardMA <- function(ser,N) {
	# "Forward Moving Average": what is the mean of the next N values from
	# t (including t itself) for a series. This probably could be done in 2 lines,
	# with a moving average and a "lead" operation. I will use brute force.
	x <- coredata(ser)
	t <- time(ser)
	L <- length(x)
	# preallocate output
	y <- rep(NA,(L - (N-1)))
	for (pos in 1:(L-(N-1))){
		m <- mean(x[pos:(pos+(N-1))])
		y[pos] <- m
	}
	out <- xts(y,order.by=t[1:(L-(N-1))])
}

MA <- function(ser,N,na.rm=F) {
	# There probably already is a function, could not find it.
	x <- coredata(ser)
	t <- time(ser)
	L <- length(x)
	# preallocate output
	y <- rep(NA,(L - (N-1)))
	for (pos in 1:(L-(N-1))){
		m <- mean(x[pos:(pos+(N-1))],na.rm=na.rm)
		y[pos] <- m
	}
	out <- xts(y,order.by=t[(1+(N-1)):L])
}

normalvol <- function(ser, N){
  chg <- diff(ser,1)
  vol_val <- 100*runSD(coredata(chg), n=N)
  out <- xts(vol_val, order.by=time(chg))
  return(out)
}

pchange <- function(x,N){
return( 100*(-1 + x/lag(x,N)))
} 

ROC <- function(x,N,freq){
  if (freq=="W"){
    freqN <- 52
  }
	if(freq=="M"){
		freqN <- 12
	}
  if (freq=="Q"){
    freqN <- 4
  }
  if (freq=="A"){
    freqN <- 1
  }
	chg <- x/lag(x,N)
	annlzd <- chg ^(freqN/N)
	return (100*(annlzd-1))
}

GrowthExtrap <- function(ser,g){
  x = coredata(ser)
  for (i in 2:length(x)){
    x[i] = x[i-1]*(1+g)
  }
  return(xts(x,order.by=time(ser)))
}

AdaptExp <- function(ser,a){
  # NOTE: This function does not handle NA or NULL; need to first
  # strip such data
  t = time(ser)
  x = coredata(ser)
  # Initialise output series; first value equals first input
  y = AdaptExp_Raw(x,a)
  out = xts(y,order.by=t)
  return(out)
}

AdaptExp_Raw<- function(x,a){
  # Initialise output series; first value equals first input
  y = x  
  for (i in 2:length(x)){
    y[i] = (1-a)*y[i-1] + a*x[i]
  }
  return(y)
}

MovingMax <-function(x){
  y = x
  for (i in 2:length(x)){
    y[i] = max(y[i-1], x[i])
  }
  return(y)
}
###########################################################


SetXAxis <- function(pp,start,numyears=1){
  if (is.character(numyears)){
    ddate = numyears
  }
  else{
    y = as.numeric(year(Sys.Date())) + numyears
    ddate = paste(as.character(y),"-01-01",sep="")
  }
  ylim = pp$coordinates$limits$y
  # Some dimwits made expand=TRUE default.
  # pp < pp + scale_x_date(limits=c(as.Date(start),as.Date(ddate)))
  pp <- pp + coord_cartesian(xlim=as.Date(c(start,ddate)), ylim=ylim, expand=FALSE,
                             default=TRUE)
  return(pp)
}

SetYAxis <- function(pp, mmin, mmax){
  # print(c(mmin, mmax))
  pp <- pp + coord_cartesian(ylim=c(mmin, mmax), expand=FALSE, default=TRUE)
  return(pp)
}

AddText <-function(pp,xpos,ypos,txt){
  pp <- pp + annotate("text",x=as.Date(xpos),y=ypos,size=2,label=txt)
  return(pp)
}

# InsertFootnote <- function(foottext,footnote_y=2){
# # Footnote
# size = .8
# color = grey(.05)
# righttext <- GetFootText()
# 
# pushViewport(viewport())
# grid.text(label=foottext,
# 	x = 0,
#              y= unit(footnote_y, "mm"),
#              just=c("left", "bottom"),
#              gp=gpar(cex= size, col=color))
# grid.text(label=righttext,
# 	x = unit(1,"npc") - unit(footnote_y, "mm"),
#              y= unit(footnote_y, "mm"),
#              just=c("right", "bottom"),
#              gp=gpar(cex= size, col=color))
# 
# popViewport()
# }


InsertFootnote <- function(foottext,footnote_y=2){
  # Footnote
  size = .6
  color = grey(.05)
  righttext <- GetFootText()
  
  pushViewport(viewport())
  grid.text(label=foottext,
            x = unit(3, "mm"),
            y= unit(footnote_y, "mm"),
            just=c("left", "bottom"),
            gp=gpar(cex= size, col=color))
  grid.text(label=righttext,
            x = unit(1,"npc") - unit(2, "mm"),
            y= unit(footnote_y, "mm"),
            just=c("right", "bottom"),
            gp=gpar(cex= size, col=color))
  
  popViewport()
}



ResizeText <- function(pp){
  pp <- pp + theme(plot.title=element_text(size=10,family="serif"),
                   axis.title=element_text(size=8,lineheight=rel(2),family="serif",colour="black"),
                   axis.text=element_text(size=8,family="serif",colour="black"),
                   legend.text=element_text(size=7,lineheight=rel(1),family="serif"),
                   legend.title=element_text(size=7,lineheight=rel(.8),family="serif"),
                   legend.key.width = unit(.6, "line"),
                   legend.key.height = unit(.6, "line")
  )
  pp <- AddWatermark2(pp)
  return(pp)
}

PlotFromLowLevel <- function(p1,fname="tmp.png",foottext="",tiny=F,footnote_y = 2){

  r = GetRes()
  p1 <- ResizeText(p1)
  fname = paste(GetImgDir(),fname, sep='')
  print(paste("Writing:",fname))

  png(fname,width=round(4.5*r),height=round(3*r),res=r)
  
  p1 = p1 + theme(plot.margin= unit(c(0.05, .15, .5, .2), "cm"))
  print(p1)
  InsertFootnote(foottext,footnote_y)
  dev.off() 
  print(p1)
  InsertFootnote(foottext,footnote_y)  
}

Plot2FromLowLevel <- function(p1,p2,fname="tmp.png",foottext="")
{
  r = GetRes()
  p1 <- ResizeText(p1)
  p2 <- ResizeText(p2)
  fname = paste(GetImgDir(),fname, sep='')
  print(paste("Writing:",fname))
  png(fname,width=round(4.5*r),height=round(3.75*r),res=r)
  grid.arrange(p1,p2,ncol=1)
  InsertFootnote(foottext)
  dev.off()
  grid.arrange(p1,p2,ncol=1)
  grid.arrange(p1,p2,ncol=1)
  InsertFootnote(foottext)  
}

Plot3FromLowLevel <- function(p1,p2,p3,fname="tmp.png",foottext="",seekingAlpha=F){
	
	fname = paste(GetImgDir(),fname, sep='')
	print(fname)
	p1 <- ResizeText(p1)
	p2 <- ResizeText(p2)
	p3 <- ResizeText(p3)
	r = GetRes()
	png(fname,width=round(4.5*r),height=round(5.25*r),res=r)
	
	grid.arrange(p1,p2,p3,ncol=1)
	InsertFootnote(foottext,seekingAlpha)
	dev.off()
	grid.arrange(p1,p2,p3,ncol=1)
	
	InsertFootnote(foottext,seekingAlpha)  
}


AutoY <- function(pp, ser){
  mmin <- min(ser)
  mmax <- max(ser)
  rng <- mmax - mmin
  if (rng==0){
    rng = 1
  }
  mmin = mmin - rng/10
  mmax = mmax + rng/10
  return (SetYAxis(pp, mmin, mmax))
  
}

PlotLowLevel1 <- function(ser,ylab="",main="",show_watermark=T){
dates <- time(ser)

valz <- coredata(ser)
xx <- data.frame(dates,valz)
names(xx) <- c("dates","valz")
pp <- ggplot(xx,aes(x=dates,y=valz)) + geom_line()
if (show_watermark){
  pp <- AddWatermark(pp,x=dates[1],y=-Inf)
	#pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=.8,family="Impact")
}
pp <- pp + geom_line()
pp <- AutoY(pp, ser)
pp <- pp + ylab(ylab)
pp <- pp + theme(axis.title.x = element_blank()) + theme(plot.title = element_text(hjust = 0.5))
pp <- pp + ggtitle(main)
return(pp)
}

PlotLowLevel1NUM <- function(ser,ylab="",main="",show_watermark=T){
  dates <- 1970 +(as.numeric(time(ser))/365.25)
  valz <- coredata(ser)
  xx <- data.frame(dates,valz)
  names(xx) <- c("dates","valz")
  pp <- ggplot(xx,aes(x=dates,y=valz)) + geom_line()
  if (show_watermark){
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=.8)
  }
  pp <- pp + geom_line()
  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  return(pp)
}

PlotLowLevel2 <- function(ser1,ser2,legend=c("series1","series2"),
                          ylab="",main="",legendpos=c(.8,.8),
                          hasmarker=F,monocolor=F,legendhead=""){
  dates <- c(time(ser1),time(ser2))
  valz <- c(coredata(ser1),coredata(ser2))
  colors <-factor(c(
	  rep("s1",length(time(ser1))),
	  rep("s2",length(time(ser2)))
  ))

  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  if(monocolor){
    pp <- ggplot(xx,aes(x=dates,y=valz))
    pp <- pp + geom_line(aes(linetype=colors))
    pp <- pp + scale_linetype_manual(legendhead,values=c(1,2))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)    
  }
  else{
  if(hasmarker){
    pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    
    pp <- pp + geom_line() + geom_point(size=2.5)
  }
  else{
    pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors,linetype=colors))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)
    #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
    pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
    pp <- pp + geom_line()
  }
  
  pp <- pp + scale_colour_manual(legendhead,values=c("black","red"))
  }
  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}
# PlotLowLevel2 <- function(ser1,ser2,legend=c("series1","series2"),
#                           ylab="",main="",legendpos=c(.8,.8),
#                           hasmarker=F,monocolor=F,legendhead=""){
#   dates <- c(time(ser1),time(ser2))
#   valz <- c(coredata(ser1),coredata(ser2))
#   colors <-factor(c(
#     rep("s1",length(time(ser1))),
#     rep("s2",length(time(ser2)))
#   ))
#   
#   levels(colors) = legend
#   xx <- data.frame(dates,valz,colors)
#   if(monocolor){
#     pp <- ggplot(xx,aes(x=dates,y=valz))
#     pp <- pp + geom_line(aes(linetype=colors))
#     pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
#     pp <- AddWatermark(pp,x=dates[1],y=-Inf)    
#   }
#   else{
#     if(hasmarker){
#       pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors,linetype=colors))
#       pp <- AddWatermark(pp,x=dates[1],y=-Inf)
#       pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
#       #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
#       
#       pp <- pp  + geom_point(size=2.5)
#     }
#     else{
#       pp <- ggplot(xx,aes(x=dates,y=valz,linetype=colors,colour=colors))
#       pp <- AddWatermark(pp,x=dates[1],y=-Inf)
#       #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
#       pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
#     }
#     
#     pp <- pp + scale_colour_manual(legendhead,values=c("black","red"))
#   }
#   pp <- pp + ylab(ylab)
#   pp <- pp + theme(axis.title.x = element_blank())
#   pp <- pp + ggtitle(main)
#   pp <- pp + theme(legend.position=legendpos)
#   return(pp)
# }


# PlotLowLevel3 <- function(ser1,ser2,ser3,legend=c("series1","series2","series3"),
#                           ylab="",main="",legendpos=c(.8,.7),
#                           hasmarker=F,monocolor=F,legendhead=""){
#   dates <- c(time(ser1),time(ser2),time(ser3))
#   valz <- c(coredata(ser1),coredata(ser2),coredata(ser3))
#   colors <-factor(c(
#     rep("s1",length(time(ser1))),
#     rep("s2",length(time(ser2))),
#     rep("s3",length(time(ser3)))
#   ))
#   
#   levels(colors) = legend
#   xx <- data.frame(dates,valz,colors)
#   if(monocolor){
#     pp <- ggplot(xx,aes(x=dates,y=valz))
#     pp <- pp + geom_line(aes(linetype=colors))
#     pp <- pp + scale_linetype_manual(legendhead,values=c(1,2,3))
#     pp <- AddWatermark(pp,x=dates[1],y=-Inf)    
#   }
#   else{
#     if(hasmarker){
#       pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
#       pp <- AddWatermark(pp,x=dates[1],y=-Inf)
#       #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
#       
#       pp <- pp + geom_line() + geom_point(size=2.5)
#     }
#     else{
#       pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
#       pp <- AddWatermark(pp,x=dates[1],y=-Inf)
#       #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
#       
#       pp <- pp + geom_line()
#     }
#     
#     pp <- pp + scale_colour_manual(legendhead,values=c("black","red","blue"))
#   }
#   pp <- pp + ylab(ylab)
#   pp <- pp + theme(axis.title.x = element_blank())
#   pp <- pp + ggtitle(main)
#   pp <- pp + theme(legend.position=legendpos)
#   return(pp)
# }
PlotLowLevel3 <- function(ser1,ser2,ser3,legend=c("series1","series2","series3"),
                          ylab="",main="",legendpos=c(.8,.7),
                          hasmarker=F,monocolor=F,legendhead=""){
  dates <- c(time(ser1),time(ser2),time(ser3))
  valz <- c(coredata(ser1),coredata(ser2),coredata(ser3))
  colors <-factor(c(
    rep("s1",length(time(ser1))),
    rep("s2",length(time(ser2))),
    rep("s3",length(time(ser3)))
  ))
  
  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  if(monocolor){
    pp <- ggplot(xx,aes(x=dates,y=valz))
    pp <- pp + geom_line(aes(linetype=colors))
    pp <- pp + scale_linetype_manual(legendhead,values=c(1,2,3))
    pp <- AddWatermark(pp,x=dates[1],y=-Inf)    
  }
  else{
    if(hasmarker){
      pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors))
      pp <- AddWatermark(pp,x=dates[1],y=-Inf)
      #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
      
      pp <- pp + geom_line() + geom_point(size=2.5)
    }
    else{
      pp <- ggplot(xx,aes(x=dates,y=valz,colour=colors,linetype=colors))
      pp <- AddWatermark(pp,x=dates[1],y=-Inf)
      #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
      
      #pp <- pp + geom_line(size=1.5)
      pp <- pp + scale_linetype_manual(legendhead,values=c(1,6,2))
      
    }
    
    pp <- pp + scale_colour_manual(legendhead,values=c("black","red","blue"))
  }
  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}


StackedBar3 <- function(ser1,ser2,ser3,legend=c("series1","series2","series3"),
                          ylab="",main="",legendpos=c(.8,.7),
                          legendhead="",convert_numeric=FALSE){
  dates <- c(time(ser1),time(ser2),time(ser3))
  if (convert_numeric){
    dates = as.numeric(year(dates)) + as.numeric(month(dates))/12
  }
  valz <- c(coredata(ser1),coredata(ser2),coredata(ser3))
  colors <-factor(c(
    rep("s1",length(time(ser1))),
    rep("s2",length(time(ser2))),
    rep("s3",length(time(ser3)))
  ))
  
  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  pp <- ggplot(xx,aes(x=dates,y=valz,fill=colors)) +
    geom_bar(stat="identity") + guides(fill=guide_legend(reverse=TRUE)) +
    scale_fill_manual(legendhead,values=c("red","green",BondEconomicsBlue()))
  
  pp <- AddWatermark(pp,x=dates[1],y=-Inf)
      #pp <- pp + annotate("text",x=dates[1],y=-Inf,label="bondeconomics.com",color="white",vjust=-.4,hjust=-.05,size=18,alpha=0.8)
  pp <- pp + scale_colour_manual(legendhead,values=c("black","red","blue"))

  pp <- pp + ylab(ylab)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
}

# May need to do this to get extra fonts...
#library(extrafont)
#font_import()
#loadfonts(device="win")

AddWatermark_orig <- function(pp,xx,yy)
{
#   annotate("text", x = Inf, y = -Inf, label = "PROOF ONLY",
#            hjust=1.1, vjust=-1.1, col="white", cex=6,
#            fontface = "bold", alpha = 0.8)  
#   
  
  pp <- pp + annotate("text",x=xx,y=yy,label="BondEconomics.com",color="#F7F7F7",vjust=-.4,hjust=-.1,size=9,alpha=0.8,family="Impact") #,family="Courier New")  
  return(pp)
}

AddWatermark <- function(pp,x,y,hjust=-.1)
{
  pp <- pp + annotate("text",x,y,label="BondEconomics.com",color="#F7F7F7",vjust=-.4,hjust=hjust,size=9,alpha=0.8,family="Impact")  
  return(pp)
}

AddWatermark2 <- function(pp)
{
#   lims <- pp$coordinates
#   x = lims$limits$x
#   print(x[1])
  return(pp)
}

