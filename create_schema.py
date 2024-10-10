from sqlalchemy import inspect
from database import engine, Base
from models import Location, PostalCode, OneMapResponse
import os
import json
from settings import json_file

inspector = inspect(engine)
default_schema = inspector.get_schema_names()[0]
tbl_list = inspector.get_table_names(schema=default_schema)
location_exist = Location.__tablename__ in tbl_list
postalcode_exist = PostalCode.__tablename__ in tbl_list
onemapr_exist = OneMapResponse.__tablename__ in tbl_list
if not (location_exist and postalcode_exist and onemapr_exist):
  Base.metadata.create_all(bind=engine)

if not os.path.exists(json_file):
  with open(json_file, 'w') as fp:
    json.dump([1, 10000], fp)
    fp.close()
