# Generated from DQL.g4 by ANTLR 4.6
from antlr4 import *
if __name__ is not None and '.' in __name__:
    from .DQLParser import DQLParser
else:
    from DQLParser import DQLParser


# This class defines a complete listener for a parse tree produced by DQLParser.
class DQLListener(ParseTreeListener):

    # Enter a parse tree produced by DQLParser#query.
    def enterQuery(self, ctx: DQLParser.QueryContext):
        pass

    # Exit a parse tree produced by DQLParser#query.
    def exitQuery(self, ctx: DQLParser.QueryContext):
        pass

    # Enter a parse tree produced by DQLParser#expr.
    def enterExpr(self, ctx: DQLParser.ExprContext):
        pass

    # Exit a parse tree produced by DQLParser#expr.
    def exitExpr(self, ctx: DQLParser.ExprContext):
        pass

    # Enter a parse tree produced by DQLParser#inExpr.
    def enterInExpr(self, ctx: DQLParser.InExprContext):
        pass

    # Exit a parse tree produced by DQLParser#inExpr.
    def exitInExpr(self, ctx: DQLParser.InExprContext):
        pass

    # Enter a parse tree produced by DQLParser#orExpr.
    def enterOrExpr(self, ctx: DQLParser.OrExprContext):
        pass

    # Exit a parse tree produced by DQLParser#orExpr.
    def exitOrExpr(self, ctx: DQLParser.OrExprContext):
        pass

    # Enter a parse tree produced by DQLParser#equalExpr.
    def enterEqualExpr(self, ctx: DQLParser.EqualExprContext):
        pass

    # Exit a parse tree produced by DQLParser#equalExpr.
    def exitEqualExpr(self, ctx: DQLParser.EqualExprContext):
        pass

    # Enter a parse tree produced by DQLParser#value.
    def enterValue(self, ctx: DQLParser.ValueContext):
        pass

    # Exit a parse tree produced by DQLParser#value.
    def exitValue(self, ctx: DQLParser.ValueContext):
        pass
