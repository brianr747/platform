# Utility functions
# Figure out to make a pcakage later...

library(data.table)

#' Create a data.frame with start and end dates where an indicator
#' series = 1.
#' 
#' Based on https://stackoverflow.com/questions/45288217/r-pick-up-the-starting-date-and-ending-date-of-the-recession-period
#' 
#' @param ser xts series.
#' @return data.frame
indicator_to_dates <- function(ser){
  indicator = coredata(ser)
  ddates = time(ser)
  df = data.frame(ddates, indicator)
  names(df) = c('ddates', 'indicator')
  out_DF = data.table(df)[, .(min(ddates), max(ddates)), by = .(rleid(indicator), indicator)][
    indicator == 1, .(Start = V1, End = V2)]
  return(out_DF)
}

OnePanelChart <- function(p1,fname="tmp.png",foottext="",footnote_y = 2){
  
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


TwoPanelChart <- function(p1,p2,fname="tmp.png",foottext="")
{
  r = GetRes()
  p1 <- ResizeText(p1)
  p2 <- ResizeText(p2)
  p1 = p1 + theme(plot.margin= unit(c(0.05, .15, .3, .2), "cm"))
  p2 = p2 + theme(plot.margin= unit(c(0.05, .15, .5, .2), "cm"))
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

Plot1Ser <- function(ser, ylab="",main="",show_watermark=T,has_marker=F, 
                     startdate=NULL){
  if (!is.null(startdate)){
    if (!endsWith(startdate, '/')){
      startdate = paste(startdate, '/', sep='')
    }
    ser = ser[startdate]
  }
  # Build data data.frame
  pp <- StartPlot()
  return(PlotWork1(pp, ser, ylab,main,show_watermark,has_marker))
}

Plot2Ser <- function(ser1,ser2, legend=c("series1","series2"),
                     ylab="",main="",legendpos=c(.8,.8),
                     hasmarker=F,legendhead="", startdate=NULL){
  if (!is.null(startdate)){
    if (!endsWith(startdate, '/')){
      startdate = paste(startdate, '/', sep='')
    }
    ser1 = ser1[startdate]
    ser2 = ser2[startdate]
    
  }
  pp <- StartPlot()
  return (PlotWork2(ser1,ser2, legend,
                    ylab, main,legendpos,
                    hasmarker,legendhead))
  
}

ShadeBars1 <- function(ser, indic, ylab="",main="",show_watermark=T,has_marker=F, 
                       startdate=NULL){
  # Based on http://jeffreybreen.wordpress.com/2011/08/15/recession-bars/
  if (!is.null(startdate)){
    if (!endsWith(startdate, '/')){
      startdate = paste(startdate, '/', sep='')
    }
    ser = ser[startdate]
    indic = indic[startdate]
  }
  # Build data data.frame

  pp <- StartPlot()
  shade_intervals = indicator_to_dates(indic)
  pp = pp + geom_rect(data=shade_intervals, aes(xmin=Start, xmax=End, ymin=-Inf, ymax=+Inf), fill='pink', alpha=0.4)
  return(PlotWork1(pp, ser, ylab,main,show_watermark,has_marker))
}

ShadeBars2 <- function(ser1,ser2,indic, legend=c("series1","series2"),
                       ylab="",main="",legendpos=c(.8,.8),
                       hasmarker=F,legendhead="", startdate=NULL){
  if (!is.null(startdate)){
    if (!endsWith(startdate, '/')){
      startdate = paste(startdate, '/', sep='')
    }
    ser1 = ser1[startdate]
    ser2 = ser2[startdate]
    indic = indic[startdate]
  }
  pp <- StartPlot()
  shade_intervals = indicator_to_dates(indic)
  pp <- pp + geom_rect(data=shade_intervals, aes(xmin=Start, xmax=End, ymin=-Inf, ymax=+Inf), 
                       fill='pink', alpha=0.4)
  return (PlotWork2(pp, ser1,ser2, legend,
                    ylab, main,legendpos,
                    hasmarker,legendhead))
  
}


StartPlot <- function(){
  pp <-   ggplot() + annotation_custom(textGrob("BondEconomics.com", x=.5, y = .2, 
                  gp=gpar(col="#F7F7F7", fontsize=30,alpha=0.8,fontfamily="Impact")))
  return(pp)
}


PlotWork1 <- function(pp, ser, ylab="",main="",show_watermark=T,has_marker=F){
  datez = time(ser)
  series.df = data.frame(date=datez,val=coredata(ser))
  names(series.df) <- c("date","val")  # Why is this necessary?
  # Turn the indicator variable into a start/end data.frame
  pp <- pp + geom_line(data=series.df, aes(x=date,y=val))
  if (has_marker){
    pp <- pp + geom_point(aes(x=date,y=val))
  }
  if (show_watermark){
    # pp <- AddWatermark(pp,x=-Inf,y=-Inf)
  }
  pp <- pp + ylab(ylab)
  pp <- AutoY(pp, ser)
  ylim = pp$coordinates$limits$y
  xlim = c(min(datez), max(datez))
  xlim[2] = xlim[1] + 1.1*(xlim[2] - xlim[1])
  pp <- pp + coord_cartesian(xlim=xlim, ylim=ylim, expand=FALSE,
                             default=TRUE)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main) + theme(plot.title = element_text(hjust = 0.5))
  return(pp)
}

PlotWork2 <- function(pp, ser1,ser2, legend=c("series1","series2"),
                     ylab="",main="",legendpos=c(.8,.8),
                     hasmarker=F,legendhead="", startdate=NULL){
  dates <- c(time(ser1),time(ser2))
  valz <- c(coredata(ser1),coredata(ser2))
  colors <-factor(c(
    rep("s1",length(time(ser1))),
    rep("s2",length(time(ser2)))
  ))
  
  levels(colors) = legend
  xx <- data.frame(dates,valz,colors)
  
  if(hasmarker){
    pp <- pp + geom_line(data=xx,aes(x=dates,y=valz,colour=colors, linetype=colors))
    pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
    pp <- pp + scale_colour_manual(legendhead,values=c("black","red"))
    pp <- pp + geom_point(data=xx, aes(x=dates, y=valz, shape=colors), size=2.5)
    pp <- pp + scale_shape_manual(legendhead, values=c(1, 2))
    
  }
  else{
    pp <- pp + geom_line(data=xx,aes(x=dates,y=valz,colour=colors,linetype=colors))
    pp <- pp + scale_linetype_manual(legendhead,values=c(1,6))
    pp <- pp + scale_colour_manual(legendhead,values=c("black","red"))
  }
  
  pp <- pp + ylab(ylab)
  pp <- AutoY(pp, valz)
  pp <- pp + theme(axis.title.x = element_blank())
  pp <- pp + ggtitle(main)  + theme(plot.title = element_text(hjust = 0.5))
  pp <- pp + theme(legend.position=legendpos)
  return(pp)
  
}
  





