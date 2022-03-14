# Dashboard Connected to Heroku
Progress:
- Survey questions and responses all in PSQL databases
  - updated through scripts/load.py
- connected Heroku with Flexmonster API, runs locally if PSQL databases included
  - https://heroku-dashboard-4020.herokuapp.com/
- PSQL queries links between databases
- Functioning pivot tables

To Do:
- improve security
  - remove csv files from scripts
  - make website only accessible after logging into admin
- update Flexmonster API with slices; include multiple tables
- move Bokeh visualizations to the same site, and add interactive functions