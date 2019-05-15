# platform
*Platform to download, manipulate and plot data. Mainly Python, with some R.*

Python 3.7 is needed (possibly 3.6); I use variable type hints which are not supported
by 3.5.

(I expect to get some collaboration on this project. I am using it for my own research, and 
I am working off the MASTER branch. If there are other users, I will switch to a 
MASTER/DEVELOPMENT  structure, so that my work doesn't break other people's work. I would
argue that it is too soon for anyone else to adopt as a work platform, unless 
they want to either go off in their own direction, or willing to keep up with the
design changes that will hit until the project structure matures. - Brian R)

## Features

Please note that all features listed are minimal implementations. However, they offer an idea
of where this project is going.

### Providers
"Single series" interface only; there will be table query support (for pandasdmx).

- "User Series": Series that are calculated by Python code dynamically
  on request.
- DB.nomics
- FRED (St. Louis Fed)
- CANSIM manual downloaded table (CSV) parsing.
- Quandl.
- Australian Bureau of Statistics via Excel.
- Reserve Bank of Australia (RBA) via Excel.

### Databases

- TEXT: Save each series as a text file in a local directory. This is
good enough for a casual user, and is useful for debugging and unit testing.
- SQLITE: The SQLite database is supported. The SQL interface
will be refactored heavily once the rest of the platform is covered with unit tests. A base class
will handle the high level logic, and then sub-classes will deal with the SQL language-specific 
details.

Meta-data support is extremely minimal. Once the SQL design is stable, will add more fields.

(Note: Starting with sqlite3, since that is installed with Python. Will worry 
about compatability with other SQL formats later.)

### Dynamic Loading

Series are loaded with a single *fetch()* command that sits between user
code and the underlying API's. This means that there is only a single
command for most end users to worry about.

The *fetch()* command is dynamic; the ticker is a combination
of the Provider and the Provider-specific ticker. (Once SQL database
support is added, users can configure friendly local tickers that are
mapped automatically to the clunkier provider tickers.)

- If the requested series does not exist, the system goes to 
the Provider and fetches it. (This is either an API call, or 
parsing a downloaded table, as in the CANSIM_CSV interface.)
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

### Other Languages
- *R* can directly trigger the Python dynamic fetching code, using 
reticulate. An example is given. (I have terrible legacy code in a
side folder.)

### Programming Support
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
- Unit test coverage has started. The core of the platform should eventually
have 100% coverage (other than some obviously non-testable code), while
the extensions are likely to have spotty coverage. No clean way to test
external API's other than finding people who want to develop a mock
framework that covers practically everything (providers and databases).

### Analysis Support

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
a library of charts, that can be configured/customised ("chart talk")
to create particular images for publication.

On the analytics side, I might try to interface with my *simple_pricers*
module, or if I am ambitious, *quantlib*. Needless to say, my focus
would be on fixed income calculations (e.g., calculating total returns
from par coupon data, forward rate approximations, etc.)

## Version 1.0

I hope to reach "Version 1.0" "soon." There are two areas that need to be
completed.

**1. Metadata.** [Updated 2109-05-15] Metadata support has been expanded, covering the most important
common fields - series name, series description. Without that information, users have almost no
idea what series represent (as I discovered on my old platform), and are forced to keep going back
to the provider web pages to get definitions. What is missing is the dictionary of provider-specific
(or even table-specific) of key/value pairs. Rather than map those metadata schemes to a common one
(which is a massive time sink), just preserve the provider scheme as-is. Since the number of
metadata fields is variable, this is painful for SQL tables. I will dump each entry into a single
table, and we can worry about creating "provider tables" later. (The problem with putting each entry
on a separate row is that there is no good way to search over them naturally.)

**2. Unit Test Coverage.** I want to get *econ_platform_core* to 100% unit test
coverage (with some areas skipped). Once this is in place, it will be possible for
users to use the code and know that they have not broken anything when they
make changes. Covering the extensions is an eventual objective, but most of
the non-core code is going to be hard to unit test anyway. (At the time of writing, coverage
is less than 100%, but in good shape. A couple of end-to-end tests are doing a lot of the coverage,
and that will need to be replaced by more granular testing.)

**3. Cleanup.** Some class names and data structure names need to be cleaned up. This probably 
should be done before people start using it. (I can refactor a variable name change in PyCharm 
fairly easily, but this will not be available for new users using text editors to develop.)

After this in place, the programming structure should be stable. All that
happens is that extensions are added. For example, financial market users 
will need SQL table structure that has multiple data types for a security in
a single table. That would just be a new "database extension" that might re-use
existing code, but it would run independently of the existing single-column
database structure.

## Big Refactoring (1)

**UPDATE 2019-05-09** The refactoring discusses here has been completed.

The refactoring has been completed. The package has been renamed and split into 
*econ_platform_core* and *econ_platform*. 

## Comments

With a fair amount of effort, users could replicate my examples. However, there will be example wrappers for various web interfaces
which may make things slightly simpler to work with.

I may write a book on research platform construction; at which point this repository would be beefed up.

My plotting code is in R. I am not that great a R programmer, and my code is a mess. I expect that I will migrate to a pure Python platform at some point. However, the R code is an example of how we can use a SQL database as the interface point between 
different languages.

There may very well be a similar package out there; I did not even bother looking. If there is a similar project, I guess I 
could switch over to working with it. However, since most of what I am doing is small wrappers on top of fairly standard
libraries, not seeing that as worthwhile. I am not too familiar with pandas, and it looks like most of what I would be doing is
within pandas already. Instead, the effort is getting everything wrapped into a high productivity environment.

## More Information

See the other text files (*.md) in this directory for more information, like
design notes.
