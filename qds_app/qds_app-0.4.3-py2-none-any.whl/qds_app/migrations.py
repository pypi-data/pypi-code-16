import datetime
import glob
import io
import logging
import os
import string
import tempfile
from mako.template import Template
from mako import exceptions
from revision import Revision


class Migrations(object):
    def __init__(self, path, context={}, current=-1):
        if(current is None):
            self.current = -1
        else:
            self.current = int(current)
        self.context = context
        self.last = None
        self.map = {}

        self.path = path
        self.base_path = os.path.dirname(os.path.realpath(__file__))

        for file_ in glob.glob("%s/[0-9]*.py" % path):
            revision = Revision(path, file_)
            self.insert(revision)

        self.context["revisions.upgraded"] = []
        self.context["revisions.downgraded"] = []

    def insert(self, revision):
        self.map[revision.revision] = revision

        if self.last is None or revision.revision > self.last.revision:
            self.last = revision

    def head(self):
        return self.map[0] if not self.map else None

    def next(self):
        return self.last.revision + 1 if self.last is not None else 0

    def list(self):
        revisions = []
        for rev in range(self.next()):
            revisions.append(rev)

        return revisions

    def upgrade(self, version=None):
        if version is not None:
            version = int(version)
            self.map[version].module.upgrade(self.context)
            return

        logging.info("current: %d", self.current)
        logging.info(self.context)
        while self.current < self.last.revision:
            self.current += 1
            logging.info("Run migration `%d`" % self.map[self.current].revision)
            self.map[self.current].module.upgrade(self.context)

        logging.info(self.context)

    def downgrade(self, revision=None, version=None):
        logging.info("current: %d", self.current)
        logging.info("revision: %s", revision)
        logging.info("version: %s", version)
        if version is not None:
            version = int(version)
            self.map[version].module.downgrade(self.context)
            return

        logging.info(self.context)
        while self.current > revision:
            logging.info("Revert migration `%d`" % self.map[self.current].revision)
            self.map[self.current].module.downgrade(self.context)
            self.current -= 1

        logging.info(self.context)

    def pending(self):
        temp_current = self.current
        revisions = []
        while temp_current < self.last.revision:
            temp_current += 1
            logging.debug("Add migration `%d`" % self.map[temp_current].revision)
            revisions.append(self.map[temp_current])

        return revisions

    def __str__(self):
        if self.head is None:
            return "<EMPTY>"
        rev_str = ""

        for rev in range(self.next()):
            rev_str += str(self.map[rev])
            rev_str += "\n"
        return rev_str

    def _generate(self, message, out_stream):
        revision = self.next()
        template = Template(filename="%s/mako_template.py" % self.base_path)

        try:
            output = template.render_unicode(up_revision=revision,
                                             create_date=datetime.datetime.now(),
                                             message=message,
                                             upgrades="""
    context["revisions.upgraded"].append(revision)
    print context""").encode("utf-8")

        except:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as ntf:
                ntf.write(
                    exceptions.text_error_template().
                    render_unicode().encode("utf-8"))
                fname = ntf.name
            raise Exception(
                "Template rendering failed; see %s for a "
                "template-oriented traceback." % fname)
        else:
            out_stream.write(output)

    def generate_str(self, message):
        out_stream = io.StringIO()
        self._generate(message, out_stream)
        return out_stream.getvalue()

    def generate(self, message):
        revision = self.next()

        message_trunc = message[:15] if len(message) > 15 else message
        message_trunc = string.replace(message_trunc, ' ', '_')
        destination_name = "%s_%s.py" % (revision, message_trunc)
        destination_path = "%s/%s" % (self.path, destination_name)

        out_stream = io.FileIO(destination_path, "wb")
        self._generate(message, out_stream)
        out_stream.close()
        logging.info("Created new migration `%s` " % destination_path)

        revision = Revision(self.path, destination_name)
        self.insert(revision)

        return destination_path
