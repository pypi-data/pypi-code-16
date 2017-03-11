from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_

from .schema import Entry, Category, Subcategory, Base


class dbHandler(object):
    __engine = None
    dbURI = None
    __session = None

    def __init__(self, dbURI):
        self.dbURI = dbURI
        self.__engine = create_engine(self.dbURI)
        self.__session = sessionmaker(bind=self.__engine)()

    def close(self):
        self.__session.close_all()
        self.__engine.dispose()

    def __repr__(self):
        return '<dbHandler %r>' % (self.dbURI)

    def create(self):
        Base.metadata.create_all(self.__engine)

    def addEntry(self, fields):
        entry = self.__session.query(Entry).\
                filter_by(name=fields["name"]).first()
        if entry:
            return
        entry = Entry(name=fields["name"])
        self.__session.add(entry)
        if "description" in fields.keys():
            entry.description = fields["description"]
        if "scriptInst" in fields.keys():
            entry.scriptInst = fields["scriptInst"]
        if "scriptUinst" in fields.keys():
            entry.scriptUinst = fields["scriptUinst"]
        if "category" in fields.keys():
            entry.category = self.__fetchCategory(fields["category"])
        if "subcategory" in fields.keys():
            entry.subcategory = self.__fetchSubcategory(fields["subcategory"])
        if len(self.__session.dirty) > 0 or len(self.__session.new) > 0:
            self.__session.commit()

    def editEntry(self, name, fields):
        entry = self.__session.query(Entry).\
                filter_by(name=name).first()
        if not entry:
            return
        if "name" in fields.keys():
            entry.name = fields["name"]
        if "description" in fields.keys():
            entry.description = fields["description"]
        if "scriptInst" in fields.keys():
            entry.scriptInst = fields["scriptInst"]
        if "scriptUinst" in fields.keys():
            entry.scriptUinst = fields["scriptUinst"]
        if "category" in fields.keys():
            entry.category = self.__fetchCategory(fields["category"])
        if "subcategory" in fields.keys():
            entry.subcategory = self.__fetchSubcategory(fields["subcategory"])
        self.__pruneCategory()
        self.__pruneSubcategory()
        self.__session.commit()

    def rmEntry(self, name):
        entry = self.__session.query(Entry).\
                filter_by(name=name).first()
        if entry:
            self.__session.delete(entry)
        if len(self.__session.deleted) > 0:
            self.__session.commit()
        self.__pruneCategory()
        self.__pruneSubcategory()
        if len(self.__session.deleted) > 0:
            self.__session.commit()

    def __fetchCategory(self, name):
        entry = self.__session.query(Category).\
                filter_by(name=name).first()
        if not entry:
            entry = Category(name=name)
        return entry

    def __fetchSubcategory(self, name):
        entry = self.__session.query(Subcategory).\
                filter_by(name=name).first()
        if not entry:
            entry = Subcategory(name=name)
        return entry

    def __pruneCategory(self):
        for entry in self.__session.query(Category).all():
            if entry.entries == []:
                self.__session.delete(entry)

    def __pruneSubcategory(self):
        for entry in self.__session.query(Subcategory).all():
            if entry.entries == []:
                self.__session.delete(entry)

    def entryNames(self):
        return(sorted([entry.name for entry in
                      self.__session.query(Entry).all()], key=str.lower))

    def categoryNames(self):
        return(sorted([entry.name for entry in
                      self.__session.query(Category).all()], key=str.lower))

    def subcategoryNames(self):
        return(sorted([entry.name for entry in
                      self.__session.query(Subcategory).all()], key=str.lower))

    def entryInfo(self, entry):
        obj = self.__session.query(Entry).filter(Entry.name == entry).first()
        if not obj:
            return None
        category = obj.category.name if obj.category else None
        subcategory = obj.subcategory.name if obj.subcategory else None
        return({"name": obj.name,
                "description": obj.description,
                "scriptInst": obj.scriptInst,
                "scriptUinst": obj.scriptUinst,
                "category": category,
                "subcategory": subcategory})

    def categoryEntries(self, category):
        entries = self.__session.query(Category).filter(
                Category.name == category).first().entries
        return(sorted(list(set([entry.name for entry in entries])),
                      key=str.lower))

    def categorySubcategories(self, category):
        entries = self.__session.query(Category).filter(
                Category.name == category).first().entries
        return(sorted(list(set([entry.subcategory.name for entry in entries])),
                      key=str.lower))

    def categorySubcategoryEntries(self, category, subcategory):
        c_entries = self.__session.query(Category).filter(
                Category.name == category).first().entries
        s_entries = self.__session.query(Subcategory).filter(
                Subcategory.name == subcategory).first().entries
        return(sorted(list(set([entry.name for entry in c_entries])
                      .intersection([entry.name for entry in s_entries])),
                      key=str.lower))
