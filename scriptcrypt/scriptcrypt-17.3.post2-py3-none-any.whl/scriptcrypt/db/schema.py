from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Entry(Base):
    __tablename__ = 'names'

    id = Column(Integer, primary_key=True)
    idCategory = Column(Integer, ForeignKey('categories.id'))
    idSubcategory = Column(Integer, ForeignKey('subcategories.id'))
    name = Column(String, unique=True)
    description = Column(Text)
    scriptInst = Column(Text)
    scriptUinst = Column(Text)
    category = relationship('Category',
                            backref='entries')
    subcategory = relationship('Subcategory',
                               backref='entries')

    def __repr__(self):
        return "<Entry(name='%s')>" % (self.name)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Category(name='%s')>" % (self.name)


class Subcategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Subcategory(name='%s')>" % (self.name)
