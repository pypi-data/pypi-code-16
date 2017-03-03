from base64 import b64decode
from rask.base import Base

__all__ = ['MapToDict']

class MapToDict(Base):
    @property
    def recipes(self):
        try:
            assert self.__recipes
        except (AssertionError,AttributeError):
            self.__recipes = {
                'bool':self.__recipe_bool,
                'int':self.__recipe_int,
                'str':self.__recipe_str,
                'unicode':self.__recipe_unicode
            }
        except:
            raise
        return self.__recipes

    def __recipe_bool(self,key,record,schema):
        return record.flags[key].value

    def __recipe_int(self,key,record,schema):
        return int(record.registers[key].value or 0)

    def __recipe_str(self,key,record,schema):
        return str(record.registers[key].value)
    
    def __recipe_unicode(self,key,record,schema):
        return b64decode(record.registers[key].value)

    def consume(self,result,record,schema,i,future):
        try:
            key = i.next()
            assert schema[key]['recipe'] in self.recipes
        except (AssertionError,KeyError):
            pass
        except StopIteration:
            future.set_result(result)
            return True
        except:
            raise
        else:
            result[key] = self.recipes[schema[key]['recipe']](
                key=key,
                record=record,
                schema=schema[key]
            )
            
        self.ioengine.loop.add_callback(
            self.consume,
            result=result,
            record=record,
            schema=schema,
            i=i,
            future=future
        )
        return None
    
    def process(self,record,schema,future):
        self.ioengine.loop.add_callback(
            self.consume,
            result={},
            record=record,
            schema=schema,
            i=iter(schema),
            future=future
        )
        return True
