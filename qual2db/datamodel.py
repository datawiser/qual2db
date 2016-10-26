'''

datamodel.py

'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Numeric, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create the declarative base
Base = declarative_base()

class Survey(Base):
	'''
	resolution in meters.
	'''
	__tablename__ = 'survey'

	id = Column(Integer, primary_key=True)
	expiration = Column(DateTime)
	name = Column(String, unique=True)

	isActive = Column(String)
	creationDate = Column(DateTime)
	lastModifiedDate = Column(DateTime)
	ownerId = Column(String)
	organizationId = Column(String)
	responseCounts = Column(Integer)