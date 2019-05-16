# Design Notes

2019-05-08 
In the middle of a big refactoring of the structure. Documentation may be out of date...

2019-05-06
I am writing these notes now as I hope to start working on other projects; I want to 
lay out my thinking for when I get back to this.

## Name Issue

The package has been renamed and split into two: "econ_platform" and
"econ_platform_core."  Although it may appear more logical to call the non-core
package "econ_platform_extensions," the expectation is that this is the package that
will always be imported; hence it has the easier-to-remember name.

## Start-Up Issue

I wanted to be able to "start up" the package with importing it. This will not
do anything that will normally fail, but will have side effects - reading config
files, importing extensions (which can monkey patch over base code).

The solution was to create a script (*start.py*) that does the set up on import. 
Purists can call the initialise package function in *econ_platform*. This will
help unit testing. 

## Circular Imports

I have run into problems with circular imports. Importing the base package needs to 
import the definitions of the abstract base classes of the provider/database wrappers,
as well as the container objects.

I had problems with having those definitions inside the "databases" and "providers" sub-packages,
which is why they migrated to the base package \_\_init__.py. 

If I cannot get that migration to work, I may move all the code inside the abstract base class
to another base class in the appropriate sub-package (e.g., "BaseProvider" and "BaseDatabase"),
and just leave the public interface definition in the base \_\_init__.py.
  
## Extensions

The objective is that coding extensions should be extremely easy to do. Ideally:
 
 - A new provider could be added solely by knowing how to download data based on a given 
 ticker, and convert the returned results to a pandas.Series.
 - A new SQL database format could be added by updating the SQL queries for the new format.
 (We could try to use a database front end, but that seems like overkill.)
 
 In order to get there, the functionality of the base classes needs to be beefed up. That will
 happen as I iterate on the design.
 
 The infrastructure for managing extensions will probably be embedded in a class.
 
 We need to distinguish two aspects to loading a Python module.
 
 1. Importing the package. Ideally, there should be no major side effects of importing a module.
 The econ_platform_core pushes that by instantiating a lot of global objects, but the instantiation
 should have little impact (empty lists, etc.).
 
 However, importing a package normally results in triggering its imports. For the *econ_platform*
 this creates a dependence upon the installation of many API modules, most of which users may
 not use. (In fact, some are extremely painful to install.) Since users should not be expected
 to install API's for features they will not use, we have to catch errors during the extension
 imports and continue on.
 
 2. Once all modules are imported, we start to initialise them. This should normally be
triggered by calling the initialise package routine in *econ_platform.* That intialisation
routine first calls the initialisation of *econ_platform_core*, which reads configuration
files, and loads the extensions in the core. With those extensions and configuration information
loaded, it is safe to go to the extensions in *econ_platform*. Users who extend the platform
should generally aim to have their extensions initialise last, so that the repository code
initialises itself first properly. Otherwise, changes to the repository code organisation 
might break user extensions. (At the time of writing, the only mechanism to ensure the order
of extension loading is the use of alphabetical order in loading the extension modules.)
 
 ## A Public Package?
 
 Although I would love that this package would have a life of its own, the reality is that
 maintenance could turn into a dog's breakfast. I already have 4 external providers, two 
 database formats, and one external language (R). Any changes on those API's would break some
 functionality of this package.
 
 (This is not a big deal if a user downloads this package and maintains it on their own. They
 would just update the interfaces they use as needed.)
 
 If everyone believed that this package was the most amazing thing in the world, the maintenance
 burden would be pushed onto the extensions: other people would supply an 
 extensions to incorporate into this package for all the other API's.
 
 (I will probably pursue that strategy within my *sfc_models* package: I will have a script that
 monkey-patches *sfc_models* functionality into the platform.) 

## Unit Tests

Unit test coverage is better, but a lot more work to do.

The split between *econ_platform_core* and *econ_platform* helps; if things are
done properly, pretty much the only code outside econ_platform_core is very difficult to 
test: calls into external API's. Unless people want to build mocks for providers,
coverage would be skipped.

At the time of writing (2019-05-10), the peripheral top-level modules in *econ_platform_core*
are covered. The big task is \_\_init__.py. I could cover most of this with just one or two
end-to-end tests, but it's better to have granular tests.

I want to switch over to using the platform for my work, so I will stop extending test
coverage for awhile.

## SQL

I have minimal SQLite support: series are overwritten completely
each time. Metadata support is improving.

The only thing I might push for is some form of series update support.Once that is
in place, I will then work on refactoring before adding features.

I think a full database wrapper package (SQLalchemy?) might be overkill. Will take a 
look when I have time.

Unless I go with a database wrapper, my plan is to beef up an abstract "SQL" class. Logic
will migrate from SQLite class to the  base class, and only the query syntax 
will be saved as  data in the subclass (if possible). Then adding a new SQL format
will just be a question of changing the syntax to be SQL-dialect specific.

## "Tickers" and Multi-Data Type Entities

Now that the SQLite code is more solid, I might move to support "local" and possibly "DataType"
tickers. 

- "Local tickers" are aliases for the more complex Provider tickers. I might create them
automatically for the Statscan Provider. (Right now, they are table|vector, but we could just use
the vector.)
- DataType tickers are typically a combination of "security|data type". This is mainly of 
interest for financial market users, but I don't have access to much in the way of such data.
Hence, it is a low priority for. It will make more sense if we have multi-column data tables. 
Financial market users probably can code their own extensions tailored for their needs.

## Provider Metadata

Different providers have series metadata with a wide variety of parameter names. We could try to
map them all to a common set of parameters (this is done for the series name and description),
but that is rather painful to do. My preference is create flexible structures to use the 
provider parameter structure; larger organisations could do their own mapping work.

My first stab at this will be to slap a dictionary of key/value pairs into a single string.
Fairly terrible data structure, but it is possible to filter for equality ('KEY=VALUE' appears).
The next version is to dynamically add columns to a table for each provider, so we have
columns matching their parameter names. (I did this on my old system with CANSIM data.) The
system can generate sprawling tables, but it should be manageable.

Although this was not a high priority, it appears to be needed for a project of mine, so it 
might be put to the top of my priority list.

