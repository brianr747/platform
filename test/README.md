# README.md: Unit Testing

This package has *a lot* of dependencies once all the extensions are included.

It should be able to function with just base Python(>3.7) and pandas. (It won't
be too useful, since there would be almost no external providers, but whatever.)

The extension imports will fail if the requisite API's were not installed. This is
not a problem for platform initialisation: it eats extension import errors. The user
is just told (if they look) that the extension was not loaded.

This will not work for unit testing; extension tests will have to be configured so that
the unit test suite will run even if some modules cannot be imported.

The solution appears to be: have modules that have import dependencies that are 
anything other than base modules or pandas throw a SkipException (?) before
any imports unless an environment variable is set to enable the test module.

This way, unit tests "work out of the box," but if people want to test extensions,
they do so at own risk...

## run_coverage.bat

This batch file runs the coverage command. Unfortunately, it is specific to my (Brian's) computer, 
as I don't put python.exe on the PATH, and the packages need to be on the PYTHONPATH for the test
imports to work.

(I might make a computer-agnostic version later.)
