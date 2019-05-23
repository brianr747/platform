"""
database_sql_alchemy.py

Implementation of a SQLalchemy database using SQLite. Has an abstract base class DatabaseSQLAlchemy,
and DatabaseAlchemySQLite. Since I am not testing on other database back ends (yet), keep most code in the base
class, but may need to refactor some to the child classes if we need to structure things differently (column
definitions, etc.) Once we get more than one back end, the base class will migrate elsewhere, probably __init__.py.

(Simpler to keep in one file for initial testing.)

Copyright 2019 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""