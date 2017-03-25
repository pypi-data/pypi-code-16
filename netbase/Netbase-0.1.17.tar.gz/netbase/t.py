class Alle(type):
    def __getattr__(cls, key):
        return "A %s"%key

try: #py3
  class MyClass(metaclass=All): pass 
except Exception as ex:
  class MyClass:
      __metaclass__ = Alle


print(MyClass.Foo)
print(MyClass.Bar)

