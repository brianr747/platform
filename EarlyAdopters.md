# EarlyAdopters.txt

## Update: 2019-05-07

There project structure is shifting quickly now, but it should stabilise "soon." In particular, a package rename is
coming, as well as a refactor that forces users to import it to get the configuration initialisation. I.e.,
instead of "import <package>," it will be "import <package>.startup"

Minimal SQLite support is in place. There is a script that copies the TEXT database into SQLite, and so 
you can import your data and look at the database structure. However, the SQL database will be refactored 
(column names changing columns added), so it is safest to work with the TEXT database so that you don't lose
your downloaded date after each refactor.

## 2019-05-02

At the time of writing, my objective is just to get a system that I can use so that I can finish my book. In particular,
I just need access to DBnomics data so that I can plot it in R. Once the book is done, I will fill out the platform.

For some time, the package may be overhauled a lot as a result of refactoring efforts. Files are moving, disappearing,
etc. as I try to see what is the most logical structure.

The structures are not yet fully in place, but the fetching is built around "databases" and "providers."

See the features in the README.md file to see the full list of providers and databases.

If you want to extend the capabilities, the package initialisation loads all Python source files (*.py) in the
"extensions" sub-package. This is how the hooks to the DB.nomics and FRED providers are added. Failures on loaded
extensions are noted, but are stepped over. This means that the package will run even if you are missing the underlying
provider/database API's, and you can extend/monkey-patch the framework without touching the source code.