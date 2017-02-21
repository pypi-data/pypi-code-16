import pytest
from objdict import ObjDict

@pytest.fixture(scope='session', autouse=True)
def copy_local_ref_db_to_working_db():
    from viewmodel.dbCopyier import DBCopier
    copy_ref_db = DBCopier()
    copy_ref_db.local("test_MV_ref", "test_MV", drop=True)

@pytest.fixture(scope='session', autouse=True)
def site():
    pass

if True:
    from viewmodel import viewMongoDB as viewModelDB
    res= ObjDict(dbname="test_MV",dbserver=None)
    viewModelDB.baseDB.connect(res)
