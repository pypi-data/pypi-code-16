import os.path
from qds_app.migrations import Migrations


def test_generate_run(tmpdir_factory):
    path = tmpdir_factory.mktemp("first_migration")
    mig = Migrations(str(path))
    migration_path = mig.generate("First Migration")
    assert(os.path.exists(migration_path))
    mig.upgrade()
    assert (len(mig.context["revisions.upgraded"]) == 1)
