# CONTRIBUTING.md

The platform structure is now much clearer as a result of the restructuring,
and so it will be easier to bring in new contributors.

As discussed in other design documents, the Python project is split into 
*econ_platform_core* and *econ_platform*. Users will normally import *econ_platform*,
as that is where almost all the extensions are. (At the time of writing, extensions
need to migrate out of the core.)

On the Python programming side, the easiest place to contribute is on the extension
side: you just need to implement a class that emulates the features of an existing
class. Adding more functionality will require a better handle on the overall design.

The objective is to allow other languages to interface to the package. I may keep 
producing my charts in *R*, for example.

(If you are unfamiliar with GIT, you can contact Brian Romanchuk (see my website
http://www.bondeconomics.com/) for a contact point). You could code extensions
(which are meant to be stand-alone) and I can incorporate them into the platform.
(Anything that touches the platform design would need to be integrated into GIT,
other than simple bug fixes or cleanup.)

Other areas:

- Documentation. (There isn't even a docs folder at the time of writing! "Who let the doc's
[sic] out! Woof Woof!")
- Programming best practices experts.
- SQL experrts.
- Pricing algorithm experts (for integration of existing libraries).
- Web/internal browser interface.
- Testing.
- Compatability testing with other OS's (I'm on Windows).
- "Publicity": for example, doing videos explaining how you use the package.
- "Open source community surveillance": is there anything out there similar? Can 
this package be incorporated into a larger project? (This project itself will
be using a lot of other projects to get their API's. This is limited at present, 
as the core needs to be built up before going crazy with extensions.)
- Open source experts who can figure out licensing issues. (I used Apache 2.0 as 
it is lightweight for notices, but this platform imports a lot of other packages,
so what's up with that?) 