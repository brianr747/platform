# platform
Platform to download, manipulate and plot data. Mainly Python, with some R. Built around a MySQL database.

This repository is mainly for my own use for now; I am transferring my platform to a new computer, and decided to do a clean up 
at the same time. In particular, the MySQL interface is not implemented.

With a fair amount of effort, users could replicate my examples. However, there will be example wrappers for various web interfaces
which may make things slightly simpler to work with.

I may write a book on research platform construction; at which point this repository would be beefed up.

My plotting code is in R. I am not that great a R programmer, and my code is a mess. I expect that I will migrate to a pure Python platform at some point. However, the R code is an example of how we can use a SQL database as the interface point between 
different languages.

There may very well be a similar package out there; I did not even bother looking. If there is a similar project, I guess I 
could switch over to working wit it. However, since most of what I am doing is small wrappers on top of fairly standard
libraries, not seeing that as worthwhile. I am not too familiar with pandas, and it looks like most of what I would be doing is
within pandas already. Instead, the effort is getting everything wrapped into a high productivity environment.

Plans.txt has some thoughts on my plans for this project.

EarlyAdopters.txt has some comments aimed at anyone who wants to use this package.