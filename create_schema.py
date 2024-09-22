from sqlalchemy import inspect
from database import engine, Base
from models import Location, PostalCode

inspector = inspect(engine)
default_schema = inspector.get_schema_names()[0]
tbl_list = inspector.get_table_names(schema=default_schema)
location_exist = Location.__tablename__ in tbl_list
postalcode_exist = PostalCode.__tablename__ in tbl_list
if not (location_exist and postalcode_exist):
    Base.metadata.create_all(bind=engine)
