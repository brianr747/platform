# README: (DATA)/statscan

This is where Statscan table zip files are downloaded into. Just place the zip here,
and then when a series from this table is fetched, the entire contents will be processed
and put into the database. (This can take time for big files.)

Files are then archived into an "archive" sub-directory. If you want to process the files again,
need to move them back into this directory.

The directory to save the files can be changed under the config settings.