from ..Symbol import Symbol

class Stock(Symbol):
    def __init__(self, ticker, name, exchange):
        Symbol.__init__(self, ticker, name, exchange)

    def getType(self):
        return 'Stock'

    def getRow(self):
        return Symbol.getRow(self)
