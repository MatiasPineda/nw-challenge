from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from init_db import db


class Regions(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Trips(db.Model):
    id = Column(Integer, primary_key=True)
    region = Column(Integer, ForeignKey('regions.id'))
    origin_latitude = Column(Numeric(precision=10, scale=7))
    origin_longitude = Column(Numeric(precision=10, scale=7))
    destination_latitude = Column(Numeric(precision=10, scale=7))
    destination_longitude = Column(Numeric(precision=10, scale=7))
    datetime = Column(DateTime)
    datasource = Column(String)
    group_label = Column(Integer, nullable=True)
