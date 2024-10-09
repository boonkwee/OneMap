from database import Base
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, TEXT, types
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func
import pytz

class TimestampMixin:
  created_at =        Column(DateTime, default=func.now(tz=pytz.timezone('Singapore')), nullable=False)
  updated_at =        Column(DateTime, default=func.now(tz=pytz.timezone('Singapore')), onupdate=func.now(), nullable=False)

class Location(TimestampMixin, Base):
  __tablename__ = 'locations'
  id =                Column(Integer, primary_key=True, index=True)
  name =              Column(String, unique=False, index=True)
  latitude =          Column(DECIMAL)
  longitude =         Column(DECIMAL)
  postal_code =       Column(String, ForeignKey('postal_code.postal_code'), nullable=True,
                             index=True, unique=False)
  postal_code_index = relationship('PostalCode', foreign_keys=[postal_code])

class PostalCode(TimestampMixin, Base):
  __tablename__ = 'postal_code'
  postal_code =       Column(String, primary_key=True, index=True)
  location_id =       Column(Integer, ForeignKey('locations.id'), nullable=True,
                             index=True)

class OneMapResponse(TimestampMixin, Base):
  __tablename__ =     'onemap_response'
  id =                Column(Integer, primary_key=True, index=True)
  total_pages =       Column(Integer)
  page_number =       Column(Integer)
  total_records =     Column(Integer)
  # record_index =      Column(Integer)
  response =          Column(TEXT)
  postal_code =       Column(String, ForeignKey('postal_code.postal_code'),
                             index=True, unique=False)
  postal_code_index = relationship('PostalCode', foreign_keys=[postal_code])


