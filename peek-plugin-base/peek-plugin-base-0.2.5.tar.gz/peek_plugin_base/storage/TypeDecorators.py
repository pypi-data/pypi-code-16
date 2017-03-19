from sqlalchemy import TypeDecorator
from sqlalchemy import VARBINARY
from sqlalchemy import cast


class PeekVarBinary(TypeDecorator):
    impl = VARBINARY

    def bind_expression(self, bindvalue):
        return cast(bindvalue, VARBINARY)