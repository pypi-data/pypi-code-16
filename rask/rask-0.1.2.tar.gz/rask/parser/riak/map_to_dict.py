from base64 import b64decode
from rask.base import Base
from rask.options import options

__all__ = ['MapToDict']

class MapToDict(Base):
    @property
    def recipes(self):
        try:
            assert self.__recipes
        except (AssertionError,AttributeError):
            self.__recipes = {
                'bool':self.__recipe_bool,
                'float':self.__recipe_float,
                'int':self.__recipe_int,
                'set':self.__recipe_set,
                'str':self.__recipe_str,
                'unicode':self.__recipe_unicode,
                'utcode':self.__recipe_utcode
            }
        except:
            raise
        return self.__recipes

    def __recipe_bool(self,key,record,schema,future):
        return future.set_result(
            record.flags[key].value
        )

    def __recipe_float(self,key,record,schema,future):
        return future.set_result(
            float(record.registers[key].value or 0)
        )

    def __recipe_int(self,key,record,schema,future):
        return future.set_result(
            int(record.registers[key].value or 0)
        )

    def __recipe_set(self,key,record,schema,future):
        return future.set_result(
            list(record.sets[key].value)
        )

    def __recipe_str(self,key,record,schema,future):
        return future.set_result(
            str(record.registers[key].value)
        )

    def __recipe_unicode(self,key,record,schema,future):
        return future.set_result(
            b64decode(record.registers[key].value)
        )

    def __recipe_utcode(self,key,record,schema,future):
        return options.utcode.decode(
            record.registers[key].value,
            future=future
        )
    
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
            def on_recipe(_):
                result[key] = _.result()
                return self.ioengine.loop.add_callback(
                    self.consume,
                    result=result,
                    record=record,
                    schema=schema,
                    i=i,
                    future=future
                )

            self.ioengine.loop.add_callback(
                self.recipes[schema[key]['recipe']],
                key=key,
                record=record,
                schema=schema[key],
                future=self.ioengine.future(on_recipe)
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
