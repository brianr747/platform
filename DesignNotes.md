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

My current test coverage is probably about 0.1% of the package; I want to move that to "100%".

How will I achieve this?

- It makes no sense to have unit tests for external provider or database API wrappers. 
Unfortunately, those are moving targets, nor do I want to inundate data providers with
garbage requests to test error handling. Either the external interfaces (including databases)
work, or they don't.
- I will have to create a "MockProvider" that just has a few fixed responses, and we can use that
to test the base class fetch/update/store functionality.
- I can use the in-memory SQLite database for database unit tests.
- The split into econ_platform_core and econ_platform helps. The coverage standard
for 100% will be first targeted for econ_platform_core; the extensions can be
sloppier.

I realised that this code will end up having a huge number of external imports.
This will mean that unit tests will fail unless the tester installs all the
packages. (The platform initialisation will just note failed extension
imports.) However, the core package really only needs standard Python libraries and
pandas. So we need to split the tests into two groups, and by default only run the
tests that do not rely on external API's. The tester can set an environment
variable to turn on the remaining tests (and deal with the import errors).

I want to get the SQLite database functioning first (so I can start working with the platform
myself); once that milestone is ready, I will try to freeze Python development until I have time
to get test coverage to "100%." (Since there will be a lot of ignored external API-dependent
code, that 100% coverage is a bit of a cheat.)

## SQL

I have minimal SQLite support: series are overwritten completely
each time. Not much in the way of meta-data.

The only thing I might push for is some form of series update support.Once that is
in place, I will then work on refactoring before adding features.

I think a full database wrapper package (SQLalchemy?) might be overkill. Will take a 
look when I have time.

Unless I go with a database wrapper, my plan is to create a "SQL" base class. Logic
will migrate from SQLite class to the  base class, and only the query syntax 
will be saved as  data in the subclass (if possible). Then adding a new SQL format
will just be a question of changing the syntax in the data configuration if needed.

## "Tickers" and Multi-Data Type Entities

One of my tasks is to standardise naming conventions. This will be easier now that I have the database;
variable names should align with database column names. (Current code needs to be standardised.)

I have used "ticker" to stand for "unique string identifier." This is OK for series with one "data type", but
when we run into financial market data, we will have things with multiple data types - stocks have prices and 
dividend yields, bonds have price and yield. It may have been more sensible to use "ticker" to refer to those
security identifiers. 

The key to the design is that we have a unique string identifier locally, as well as a unique string identifier
for queries. Even if we store related data in multi-column tables, we still need a single identifier for each column
of data. Since we will not be able to align with provider data type identifiers in our database, we still need a series-by-series mapping.

What are currently called "local tickers" will allow us to handle these multi-datatype securities. We just need to
patch in the local ticker, and they will incorporate the local multi-datatype naming convention.

I think it is necessary to create classes that manage the ticker rules, and are used 
internally as parameters. Eliminates the need for defensive coding around tickers.
Making them classes will make it easier for people to customise ticker
construction.