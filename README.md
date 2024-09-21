# Postal Code Database
This repo is a simple Database Python application that creates a sqlite3 db and pulls Singapore Postal code and the corresponding location name to the db.

## database.py
This is the file that defines the database connection. Modify this file to switch to a different type of database. I will include a connection to a working PostreSQL db in the future development.

## models.py
This is the schematic relationship of the database tables, defined using the Python Sqlalchemy library style so that the effort required to transform the fields to Python native datatype is reduce to a minimum.
The format of the style is in Sqlalchemy 1.0.

## settings.py
This file retrieves the database password, as well as access token to GMap and OneMAP API. It is designed in a way developers can fork this project and use it for themselves, but have get their own passwords and access tokens.

## pull_onemap.py
This file depends on the above files and initiates connection with OneMap dot gov dot sg to query for the necessary information.

## show_schema.py
This file uses the first three file to establish a connection and displays the table schema. If any of the components does not work. This file will fail.

## sqlite3 OneMap.ipynb
This file is a working prototype. There are slight changes to some code as it is meant to run in a Colab notebook. To use this, upload this notebook to Google Colab, set up the necessary secret keys as the passwords/access tokens and it should work.

## singapore_addresses1.db
This is a demo copy of the db, there are some sample data in the db for testing purpose. After forking this project, rename this file to singapore_addresses.db for the App to work.
