set PYTHONPATH=C:\Users\brian\PycharmProjects\platform
"c:\Program Files\Python37_64\python.exe" -m coverage  run --omit="*site-package*","test*","loc_utils.py" -m unittest discover
"c:\Program Files\Python37_64\python.exe" -m coverage report
"c:\Program Files\Python37_64\python.exe" -m coverage html