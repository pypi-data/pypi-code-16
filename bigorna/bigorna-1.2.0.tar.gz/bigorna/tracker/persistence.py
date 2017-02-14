from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bigorna.commons.config import Config


Base = declarative_base()


def create_engine(cfg: Config):
    file = cfg.db_file or ':memory:'
    db_file = 'sqlite:///%s' % file
    return sqlalchemy_create_engine(db_file, echo=False)


def get_sessionmaker(cfg: Config):
    return sessionmaker(bind=create_engine(cfg))
