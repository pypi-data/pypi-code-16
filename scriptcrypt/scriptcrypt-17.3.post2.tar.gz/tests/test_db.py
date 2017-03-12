from nose.tools import *
from tests import *
import scriptcrypt.db as mydb


def test_add_entry():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    assert db.entryInfo("name1")["name"] == "name1"
    assert db.entryInfo("name1")["description"] == "description1"
    assert db.entryInfo("name1")["category"] == "category1"
    assert db.entryInfo("name1")["subcategory"] == "subcategory1"
    assert db.entryInfo("name1")["scriptInst"] == "scriptInst1"
    assert db.entryInfo("name1")["scriptUinst"] == "scriptUinst1"
    db.editEntry("name1", {"name": "name",
                           "description": "description",
                           "scriptInst": "scriptInst",
                           "scriptUinst": "scriptUinst",
                           "category": "category",
                           "subcategory": "subcategory"})
    assert db.entryInfo("name")["name"] == "name"
    assert db.entryInfo("name")["description"] == "description"
    assert db.entryInfo("name")["category"] == "category"
    assert db.entryInfo("name")["subcategory"] == "subcategory"
    assert db.entryInfo("name")["scriptInst"] == "scriptInst"
    assert db.entryInfo("name")["scriptUinst"] == "scriptUinst"


def test_entry_names():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert "name1" in db.entryNames()
    assert "name2" in db.entryNames()
    db.rmEntry("name1")
    assert "name1" not in db.entryNames()


def test_dublicate():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert db.entryInfo("name")["description"] == "description1"
    assert not db.entryInfo("name")["description"] == "description"


def test_category_names():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert "category1" in db.categoryNames()
    assert "category2" in db.categoryNames()
    db.rmEntry("name1")
    assert "category1" not in db.categoryNames()


def test_subcategory_names():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert "subcategory1" in db.subcategoryNames()
    assert "subcategory2" in db.subcategoryNames()
    db.rmEntry("name1")
    assert "subcategory1" not in db.subcategoryNames()


def test_entry_info():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert db.entryInfo("name1")["name"] == "name1"
    assert db.entryInfo("name1")["description"] == "description1"
    assert db.entryInfo("name1")["scriptInst"] == "scriptInst1"
    assert db.entryInfo("name1")["scriptUinst"] == "scriptUinst1"
    assert db.entryInfo("name1")["category"] == "category1"
    assert db.entryInfo("name1")["subcategory"] == "subcategory1"


def test_category_entries():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category1",
                 "subcategory": "subcategory2"})
    db.addEntry({"name": "name3",
                 "description": "description3",
                 "scriptInst": "scriptInst3",
                 "scriptUinst": "scriptUinst3",
                 "category": "category3",
                 "subcategory": "subcategory3"})
    db.addEntry({"name": "name4",
                 "description": "description4",
                 "scriptInst": "scriptInst4",
                 "scriptUinst": "scriptUinst4",
                 "category": "category1",
                 "subcategory": "subcategory4"})
    assert len(db.categoryEntries("category1")) == 3
    assert "name1" in db.categoryEntries("category1")


def test_category_subcategories():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    db.addEntry({"name": "name3",
                 "description": "description3",
                 "scriptInst": "scriptInst3",
                 "scriptUinst": "scriptUinst3",
                 "category": "category3",
                 "subcategory": "subcategory3"})
    db.addEntry({"name": "name4",
                 "description": "description4",
                 "scriptInst": "scriptInst4",
                 "scriptUinst": "scriptUinst4",
                 "category": "category4",
                 "subcategory": "subcategory4"})
    assert len(db.categorySubcategories("category1")) == 1
    assert "subcategory1" in db.categorySubcategories("category1")
    assert "subcategory2" in db.categorySubcategories("category2")


def test_category_subcategory_entries():
    db = mydb.dbHandler(SQLALCHEMY_DATABASE_URI)
    db.create()
    db.addEntry({"name": "name1",
                 "description": "description1",
                 "scriptInst": "scriptInst1",
                 "scriptUinst": "scriptUinst1",
                 "category": "category1",
                 "subcategory": "subcategory1"})
    db.addEntry({"name": "name2",
                 "description": "description2",
                 "scriptInst": "scriptInst2",
                 "scriptUinst": "scriptUinst2",
                 "category": "category2",
                 "subcategory": "subcategory2"})
    assert len(db.categorySubcategoryEntries("category1",
                                             "subcategory1")) == 1
    assert "name1" in db.categorySubcategoryEntries("category1",
                                                    "subcategory1")
    assert "name2" in db.categorySubcategoryEntries("category2",
                                                    "subcategory2")
