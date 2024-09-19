from sqlalchemy import inspect
from database import engine
from pprint import pprint
inspector = inspect(engine)
schemas = inspector.get_schema_names()

for schema in schemas:
  print("schema: %s" % schema)
  for table_name in inspector.get_table_names(schema=schema):
    print("Table: %s" % table_name)
    for column in inspector.get_columns(table_name, schema=schema):
      print(f"\t{column}")