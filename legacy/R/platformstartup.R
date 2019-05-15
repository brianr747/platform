# Load the Python package econ_platform_core using reticulate
# NOTE: Need to make sure "econ_platform_core" is on the Python path.
# To do this on my development machine, I set the
# PYTHONPATH in the Renvornment.site to point at my development
# version.
# 

library(reticulate)
library(xts)

myplatform = import("econ_platform.start")
# Start logging
myplatform$LogInfo$LogDirectory = "."
myplatform$start_log()
myplatform$log_extension_status()


pfetch <- function(ticker, database="Default"){
  df = myplatform$fetch_df(ticker, database)
  ser = xts(df$series_values, order.by=as.Date(df$series_dates))
  return(ser)
}

# Get rid of the warnings about the time zone...
# options(xts_check_TZ=FALSE)

