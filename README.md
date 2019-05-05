# platform
Platform to download, manipulate and plot data. Mainly Python, with some R. Built around a MySQL database (eventually).

Python 3 only. I work on Python 3.7, and no idea about backward 
compatability issues.

This repository is mainly for my own use for now; I am transferring my platform to a new computer, and decided to do a clean up 
at the same time. In particular, the MySQL interface is not implemented.

Features

Please note that all features listed are minimal implementations. However, they offer an idea
of where this project is going.

*Providers*
"Single series" interface only; there will be table query support (for pandasdmx).

- "User Series": Series that are calculated by Python code dynamically
  on request.
- DB.nomics
- FRED (St. Louis Fed)
- CANSIM manual downloaded table (CSV) parsing.
- (Coming soon?) Quantl.

*Databases*

- TEXT: Save each series as a text file in a local directory. This is
good enough for a casual user, and is user for debugging and unit testing.

No meta-data support until the SQL interface is attacked.

*Dynamic Loading*

Series are loaded with a single *fetch()* command that sits between user
code and the underlying API's. This means that there is only a single
command for most end users to worry about.

The *fetch()* command is dynamic; the ticker is a combination
of the Provider and the Provider-specific ticker. (Once SQL database
support is added, users can configure friendly local tickers that are
mapped automatically to the clunkier provider tickers.)

- If the requested series does not exist, the system goes to 
the Provider and fetches it. (This is either an API call, or 
parsing a downloaded table, as in the CANSIM_CSV interfae.)
- If the series exists on the database, that series is returned
(at the minimum.)
- If the series is *USER* series, the appropriate Python code module
(registered by the user) will calculate the series in the same way as
an external provider API.
- TODO: If the series exists, an "update protocol" will be implemented.
(Right now, if you want to update a series, you delete the text file...)
The Provider code will decide whether it is worthwhile doing another
API query, and most queries will be incremental. This means that users
can fetch the same series 100 times in a row, and the provider API
will be hit with perhaps one API refresh call in a day. The update
protocol would be extremely important for an "industrial" multi-user
platform, but is not a pressing issue for me.

*Other Languages*
- *R* can directly trigger the Python dynamic fetching code, using 
reticulate. An example is given. (I have terrible legacy code in a
side folder.)

*Programming Support*
- Very clean interface to the *logging* module; you just call 
*start_log()* and a log file based on the module name is created in
a (configurable) log directory. 
- Highly configurable. Although hard-coded behaviour exists, it is
possible to use text configuration files to modify behaviour. Built 
with the *configparser* module. The user is encouraged to create a 
config file outside the repository so that it does not collide with
GIT.
- Automatic extension support. Other than minimal features that 
should always work, providers/databases are loaded as extensions.
If the user is missing the appropriate API modules, the extension
load will fail - but the rest of the platform is functional. (For 
example, you need an API key for the St. Louis FRED interface for
Python.)
- Users can use the extension interface to monkey-patch the platform,
so that any parts of the code that are horrifying can be replaced.
- Unfortunately, very little in the way of unit tests (although some
exist). The most important code here are 

*Analysis Support*

Since *fetch()* returns a pandas Series object, they can leverage 
the features of pandas. (Disclaimer: I am not too familiar with 
pandas, and so my pandas code may stink.) Currently, the main
advantage for analysts is *fetch()* and the ease of configuration/
logging.

- *quick_plot()* One line plotting of series. (Although there is a 
*Series.Plot()* method, I still need to call 
*matplotlib.pyplot.show()* to see it.) Eventually, look-and-feel will
be configurable with config files.

The main planned work (which will be done when heavy development 
starts) is to create classes to clean up chart management: create
a library of charts, that can be configured/customised ("chart talk*)
to create particular images for publication.

On the analytics side, I might try to interfae with my *simple_pricers*
module, or if I am ambitious, *quantlib*. Needless to say, my focus
would be on fixed income calculations (e.g., calculating total returns
from par coupon data, forward rate approximations, etc.)

**Comments**

With a fair amount of effort, users could replicate my examples. However, there will be example wrappers for various web interfaces
which may make things slightly simpler to work with.

I may write a book on research platform construction; at which point this repository would be beefed up.

My plotting code is in R. I am not that great a R programmer, and my code is a mess. I expect that I will migrate to a pure Python platform at some point. However, the R code is an example of how we can use a SQL database as the interface point between 
different languages.

There may very well be a similar package out there; I did not even bother looking. If there is a similar project, I guess I 
could switch over to working wit it. However, since most of what I am doing is small wrappers on top of fairly standard
libraries, not seeing that as worthwhile. I am not too familiar with pandas, and it looks like most of what I would be doing is
within pandas already. Instead, the effort is getting everything wrapped into a high productivity environment.



**More Information**

Plans.txt has some thoughts on my plans for this project.

EarlyAdopters.txt has some comments aimed at anyone who wants to use this package.