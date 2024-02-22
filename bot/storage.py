from sqlalchemy import create_engine, Column, Integer, Text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///bots.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()
class Bots(Base):
    __tablename__ = 'bots'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    p_id = Column(Integer)
    token = Column(Text)
    username = Column(Text)
    url = Column(Text)

metadata = MetaData()
def create_tables():
    Base.metadata.create_all(bind=engine)

Session = sessionmaker(engine)
session = Session()