import yaml
import os

try:
    with open( '../config.yaml', 'r' ) as f:
        settings = yaml.safe_load( f )
        dburl = 'postgresql://' + settings["postgreql_username"] + ':' + settings["postgreql_password"] + '@localhost/' + settings["postgres_db"] + '?client_encoding=utf8'
except IOError:
    dburl = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost:5432/dbname')

from sqlalchemy import create_engine
engine = create_engine(dburl, pool_recycle=60, encoding='utf8')
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, func, update, Text, Binary, Boolean, BigInteger, event, select, exc
from sqlalchemy.orm import sessionmaker, scoped_session
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
