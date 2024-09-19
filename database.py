from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = 'sqlite:///./singapore_addresses.db'
# DATABASE_URL = 'sqlite:////content/drive/MyDrive/singapore_addresses.db'

# engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
engine = create_engine(DATABASE_URL)
session_pool = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass
