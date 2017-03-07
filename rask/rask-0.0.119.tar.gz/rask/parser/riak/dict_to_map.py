from base64 import b64encode
from rask.base import Base

__all__ = ['DictToMap']

class DictToMap(Base):
    @property
    def recipes(self):
        try:
            assert self.__recipes
        except (AssertionError,AttributeError):
            self.__recipes = {
                'bool':self.__recipe_bool,
                'int':self.__recipe_str,
                'str':self.__recipe_str,
                'unicode':self.__recipe_unicode
            }
        except:
            raise
        return self.__recipes

    def __recipe_bool(self,key,data,record,schema):
        try:
            assert data[key]
        except AssertionError:
            record.flags[key].disable()
        except:
            raise
        else:
            record.flags[key].enable()
        return record

    def __recipe_str(self,key,data,record,schema):
        record.registers[key].assign(str(data[key]))
        return record

    def __recipe_unicode(self,key,data,record,schema):
        record.registers[key].assign(b64encode(data[key]))
        return record
    
    def consume(self,data,record,schema,i,future):
        try:
            key = i.next()
            assert schema[key]['recipe'] in self.recipes
        except (AssertionError,KeyError):
            pass
        except StopIteration:
            future.set_result(record)
            return True
        except:
            raise
        else:
            record = self.recipes[schema[key]['recipe']](
                key=key,
                data=data,
                record=record,
                schema=schema
            )

        return self.ioengine.loop.add_callback(
            self.consume,
            data=data,
            record=record,
            schema=schema,
            i=i,
            future=future
        )
    
    def process(self,data,record,schema,future):
        return self.ioengine.loop.add_callback(
            self.consume,
            data=data,
            record=record,
            schema=schema,
            i=iter(data),
            future=future
        )
