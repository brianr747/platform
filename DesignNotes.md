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