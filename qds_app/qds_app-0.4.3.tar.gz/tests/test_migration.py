import inspect
import logging
import os.path
from qds_app.migrations import Migrations


def test_empty_list(tmpdir_factory):
    path = tmpdir_factory.mktemp("empty_migrations")
    logging.info("Temp Path: %s" % path)
    mig = Migrations(str(path))
    assert(len(mig.list()) == 0)


def test_generate_first_migration(tmpdir_factory):
    path = tmpdir_factory.mktemp("first_migration")
    logging.info("Temp Path: %s" % path)
    mig = Migrations(str(path))
    migration_path = mig.generate("First Migration")
    assert(os.path.exists(migration_path))


def test_single_upgrade():
    path = "%s/fixtures/upgrade" % \
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    mig = Migrations(path)
    mig.upgrade()
    assert (len(mig.context["revisions.upgraded"]) == 1)


def test_single_downgrade():
    path = "%s/fixtures/downgrade" % \
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    mig = Migrations(path, current=5)
    revision = -1
    mig.downgrade(revision=revision)
    assert (len(mig.context["revisions.downgraded"]) == 6)


def test_single_pending():
    path = "%s/fixtures/upgrade" % \
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    mig = Migrations(path)
    pending = mig.pending()
    assert (len(pending) == 1)
