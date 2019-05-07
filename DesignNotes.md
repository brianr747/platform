# Design Notes

2019-05-06
I am writing these notes now as I hope to start working on other projects; I want to 
lay out my thinking for when I get back to this.

## Name Issue

The current name of the package is a placeholder, but I think I need to change it soon.

My preference is *economics_platform*, but open to suggestions. It will be easy to refactor
until people start using it. 

## Start-Up Issue

I want the package to be extremely efficient to use. I want to be able to do either:

    import {package/module}

or 

    from {package/module} import *

and have the package:
1) Import base modules.
2) Import extensions.
3) Load configuration information from config files.
4) Allow for automatic monkey-patching from within an extension.

Furthermore, I wanted the names of the imported functions to be short.

The problem is that (2) & (3) & (4) all have side effects, which is a disaster for
unit testing.

The solution appears to be that I will create a *script* startup.py that is inside the package.
Importing it launches the start up configuration protocol. The initialisation code
that is in \_\_init__.py will not be invoked automatically. 

It looks like this solution will cover all of my objectives, and make importing the base package
have almost no side effects (other than the declaration of abstract base classes, and initialising
the containers for database provider wrappers).

This change will break my existing example code; better to do it now than later.

## Circular Imports

I have run into problems with circular imports. Importing the base package needs to 
import the definitions of the abstract base classes of the provider/database wrappers,
as well as the container objects.

I had problems with having those definitions inside the "databases" and "providers" sub-packages,
which is why they migrated to the base package \_\_init__.py. 

If I cannot get that migration to work, I may move all the code inside the abstract base class
to another base class in the appropriate sub-package (e.g., "BaseProvider" and "BaseDatabase"),
and just leave the public interface definition in the base \_\_init__.py.

Other high level modules:
- **configuration.py** It makes sense to pull the front end to ConfigParser into a separate module.
- **utils.py** The code in utils.py are things I do all the time with standard Python code.
  It should not import any other modules from this package, so it should avoid circular
  import problems.
  
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
- The initialisation code is currently automatically triggered; I need to turn that off (as
discussed earlier).

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


