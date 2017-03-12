from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import SMALLINT
from sqlalchemy.dialects.postgresql import JSONB


Relation = declarative_base()


class Command(Relation):
    __tablename__ = 'commands'

    id =  Column(UUID,
        primary_key=True,
        name='id'
    )

    name = Column(String,
        nullable=False,
        name='name'
    )

    sid = Column(UUID,
        nullable=False,
        name='sid'
    )

    cid = Column(UUID,
        nullable=False,
        name='cid'
    )

    tid = Column(UUID,
        nullable=False,
        name='tid'
    )

    issued = Column(BigInteger,
        nullable=False,
        name='issued'
    )

    params = Column(JSONB,
        nullable=False,
        name='params'
    )

    #expires = Column(BigInteger,
    #    nullable=False,
    #    name='expires'
    #)
