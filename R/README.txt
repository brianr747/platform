README.txt
==========

This code is relatively clean R code for interfacing with myplatform.

(The *ugly* stuff is in legacy/R.)

The reticulate library is used to run Python. The only trick is that you need to get "myplatform" on the path.

Right now, just the command to do fetching is here. An experienced R programmer can take it from there. My example
code uses the functions in a library file "allfn2.R" in \legacy\R; that code is a mess, so only go there if you
want to replicate my work.

I did this by putting the appropriate PYTHONPATH setting in the Renviron.site file. (On my machine,
C:\Program Files\R\R-3.5.3\etc)

If this package ever makes the big time, it will be on PyPi, and can do installation with pip install.