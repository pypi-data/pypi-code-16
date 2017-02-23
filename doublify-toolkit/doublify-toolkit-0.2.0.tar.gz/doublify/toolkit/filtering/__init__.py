from enum import Enum

from antlr4 import CommonTokenStream, ParseTreeWalker
from antlr4.InputStream import InputStream

from DQLLexer import DQLLexer
from DQLParser import DQLParser
from DQLListener import DQLListener


class Operation(Enum):
    # Equal Expression
    #
    # * ID : value
    EQUAL = 1

    # In Expression
    #
    # * ID : ( (value)* )
    IN = 2

    # Or Expression
    #
    # * ID : { (value)* }
    OR = 3


class DQLEmitter(DQLListener):
    reply = {}

    current_filtering = []

    def enterInExpr(self, ctx):
        self.current_filtering = []

    def exitInExpr(self, ctx):
        filtering = self.current_filtering

        self.reply[ctx.ID().getText()] = {
            'operation': Operation.IN,
            'values': filtering,
        }

    def enterOrExpr(self, ctx):
        self.current_filtering = []

    def exitOrExpr(self, ctx):
        filtering = self.current_filtering

        self.reply[ctx.ID().getText()] = {
            'operation': Operation.OR,
            'values': filtering,
        }

    def enterEqualExpr(self, ctx):
        self.current_filtering = []

    def exitEqualExpr(self, ctx):
        filtering = self.current_filtering

        keyword = ctx.KEYWORD()

        if keyword:
            filtering = [True] if keyword.getText() == 'is' else [False]

        self.reply[ctx.ID().getText()] = {
            'operation': Operation.EQUAL,
            'values': filtering,
        }

    def exitValue(self, ctx):
        value = None

        if ctx.INTEGER():
            value = int(ctx.INTEGER().getText())
        elif ctx.FLOAT():
            value = float(ctx.FLOAT().getText())
        elif ctx.STRING():
            value = ctx.STRING().getText().strip('"')
        else:
            return

        self.current_filtering.append(value)


def parse_query(query):
    stream = InputStream(query)

    lexer = DQLLexer(stream)

    stream = CommonTokenStream(lexer)

    parser = DQLParser(stream)

    tree = parser.query()

    emitter = DQLEmitter()

    walker = ParseTreeWalker()
    walker.walk(emitter, tree)

    return emitter.reply
