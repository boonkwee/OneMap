from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, ForeignKey, TIMESTAMP
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func

class TimestampMixin:
  created_at = Column(DateTime, default=func.now(), nullable=False)
  updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class Location(TimestampMixin, Base):
  __tablename__ = 'locations'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=False, index=True)
  total_pages = Column(Integer)
  page_number = Column(Integer)
  latitude = Column(DECIMAL)
  longitude = Column(DECIMAL)
  postal_code = Column(String, ForeignKey('postal_code.postal_code'), nullable=True,
                       index=True, unique=False)
  postal_code_index = relationship('PostalCode', foreign_keys=[postal_code])

class PostalCode(TimestampMixin, Base):
  __tablename__ = 'postal_code'
  postal_code = Column(String, primary_key=True, index=True)
  location_id = Column(Integer, ForeignKey('locations.id'), nullable=True,
                       index=True)

