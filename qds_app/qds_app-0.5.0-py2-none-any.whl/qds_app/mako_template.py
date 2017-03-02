"""${message}

Revision ID: ${up_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Mojave.
revision = ${up_revision}
import logging
${imports if imports else ""}

def upgrade(context):
    logging.debug("Execute upgrade of `%d`" % revision)
    ${upgrades if upgrades else "pass"}


def downgrade(context):
    logging.debug("Execute downgrade of `%d`" % revision)
    ${downgrades if downgrades else "pass"}
