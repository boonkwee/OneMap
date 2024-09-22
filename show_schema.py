from sqlalchemy import inspect
from database import engine
from pprint import pprint
inspector = inspect(engine)
schemas = inspector.get_schema_names()
schemas_count = len(schemas)

for schema in schemas:
  print(f"schema: {schema} [{schemas_count}]")
  tbl_list = inspector.get_table_names(schema=schema)
  tbl_count = len(tbl_list)
  for table_name in tbl_list:
    print(f"Table: {table_name} [{tbl_count}]")
    for column in inspector.get_columns(table_name, schema=schema):
      print(f"\t{column}")
