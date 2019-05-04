# Load the Python package myplatform using reticulate
# NOTE: Need to make sure "myplatform" is on the Python path.
# To do this on my development machine, I set the
# PYTHONPATH in the Renvornment.site to point at my development
# version.
# 

library(reticulate)
library(xts)

myplatform = import("myplatform")
# Start logging
myplatform$LogInfo$LogDirectory = "."
myplatform$start_log()


pfetch <- function(ticker){
  df = myplatform$fetch_df(ticker)
  ser = xts(df$series_values, order.by=as.Date(df$series_dates))
  return(ser)
}

# Get rid of the warnings about the time zone...
# options(xts_check_TZ=FALSE)

