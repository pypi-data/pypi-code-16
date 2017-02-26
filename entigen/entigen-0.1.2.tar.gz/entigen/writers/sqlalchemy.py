from typing import Optional, List

from ..model import Entity, Property
from ..block import Block
from .python import PythonWriter

class SQLAlchemyWriter(PythonWriter, name="sqlalchemy"):
    
    block_types = ["crud"]

    def write_crud(self, entities: List[Entity]) -> Block:
        pass

    def create_block(self, block_type: str,
                     entities: Optional[List[str]]=None) -> Block:
        write_ents = [self.model.entity(name)
                      for name in entities or self.model.entity_names]

        if block_type == "crud":
            return self.write_crud(write_ents)
        else:
            raise Exception("Unknown SQLAlchemy block type '{}'"
                            .format(block_type))
