# README.md: Unit Testing

This package has *a lot* of dependencies once all the extensions are included.

It should be able to function with just base Python(>3.7) and pandas. (It won't
be too useful, since there would be almost no external providers, but whatever.)

The extension imports will fail if the requisite API's were not installed. This is
not a problem for platform initialisation: it eats extension import errors. The user
is just told (if they look) that the extension was not loaded.

This will not work for unit testing; extension tests will have to be configured so that
the unit test suite will run even if some modules cannot be imported.

I will only worry about this if other people start using the package and report unit
test problems. Installing and and uninstalling packages continuously to test the 
integrity of unit tests is not a priority for me.

(One solution is to separate out the extensions into another directory; but that
messes up my coverage analysis.)