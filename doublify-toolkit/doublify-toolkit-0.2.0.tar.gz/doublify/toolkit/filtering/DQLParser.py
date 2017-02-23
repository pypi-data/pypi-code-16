# Generated from DQL.g4 by ANTLR 4.6
# encoding: utf-8
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write('\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\r')
        buf.write(':\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\3\2')
        buf.write('\7\2\20\n\2\f\2\16\2\23\13\2\3\3\3\3\3\3\5\3\30\n\3\3')
        buf.write('\4\3\4\3\4\3\4\7\4\36\n\4\f\4\16\4!\13\4\3\4\3\4\3\5\3')
        buf.write('\5\3\5\3\5\7\5)\n\5\f\5\16\5,\13\5\3\5\3\5\3\6\3\6\3\6')
        buf.write('\3\6\3\6\3\6\5\6\66\n\6\3\7\3\7\3\7\2\2\b\2\4\6\b\n\f')
        buf.write('\2\3\3\2\t\139\2\21\3\2\2\2\4\27\3\2\2\2\6\31\3\2\2\2')
        buf.write('\b$\3\2\2\2\n\65\3\2\2\2\f\67\3\2\2\2\16\20\5\4\3\2\17')
        buf.write('\16\3\2\2\2\20\23\3\2\2\2\21\17\3\2\2\2\21\22\3\2\2\2')
        buf.write('\22\3\3\2\2\2\23\21\3\2\2\2\24\30\5\6\4\2\25\30\5\b\5')
        buf.write('\2\26\30\5\n\6\2\27\24\3\2\2\2\27\25\3\2\2\2\27\26\3\2')
        buf.write('\2\2\30\5\3\2\2\2\31\32\7\f\2\2\32\33\7\7\2\2\33\37\7')
        buf.write('\3\2\2\34\36\5\f\7\2\35\34\3\2\2\2\36!\3\2\2\2\37\35\3')
        buf.write("\2\2\2\37 \3\2\2\2 \"\3\2\2\2!\37\3\2\2\2\"#\7\4\2\2#")
        buf.write("\7\3\2\2\2$%\7\f\2\2%&\7\7\2\2&*\7\5\2\2\')\5\f\7\2(\'")
        buf.write('\3\2\2\2),\3\2\2\2*(\3\2\2\2*+\3\2\2\2+-\3\2\2\2,*\3\2')
        buf.write('\2\2-.\7\6\2\2.\t\3\2\2\2/\60\7\b\2\2\60\61\7\7\2\2\61')
        buf.write('\66\7\f\2\2\62\63\7\f\2\2\63\64\7\7\2\2\64\66\5\f\7\2')
        buf.write('\65/\3\2\2\2\65\62\3\2\2\2\66\13\3\2\2\2\678\t\2\2\28')
        buf.write('\r\3\2\2\2\7\21\27\37*\65')
        return buf.getvalue()


class DQLParser(Parser):

    grammarFileName = 'DQL.g4'

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = ['<INVALID>', "'('", "')'", "'{'", "'}'", "':'"]

    symbolicNames = [
        '<INVALID>', 'OPEN_PARENTHESES', 'CLOSE_PARENTHESES', 'OPEN_CURLY',
        'CLOSE_CURLY', 'COLON', 'KEYWORD', 'INTEGER', 'FLOAT', 'STRING', 'ID',
        'WS'
    ]

    RULE_query = 0
    RULE_expr = 1
    RULE_inExpr = 2
    RULE_orExpr = 3
    RULE_equalExpr = 4
    RULE_value = 5

    ruleNames = ['query', 'expr', 'inExpr', 'orExpr', 'equalExpr', 'value']

    EOF = Token.EOF
    OPEN_PARENTHESES = 1
    CLOSE_PARENTHESES = 2
    OPEN_CURLY = 3
    CLOSE_CURLY = 4
    COLON = 5
    KEYWORD = 6
    INTEGER = 7
    FLOAT = 8
    STRING = 9
    ID = 10
    WS = 11

    def __init__(self, input: TokenStream):
        super().__init__(input)
        self.checkVersion('4.6')
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA,
                                          self.sharedContextCache)
        self._predicates = None

    class QueryContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i: int=None):
            if i is None:
                return self.getTypedRuleContexts(DQLParser.ExprContext)
            else:
                return self.getTypedRuleContext(DQLParser.ExprContext, i)

        def getRuleIndex(self):
            return DQLParser.RULE_query

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterQuery'):
                listener.enterQuery(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitQuery'):
                listener.exitQuery(self)

    def query(self):

        localctx = DQLParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == DQLParser.KEYWORD or _la == DQLParser.ID:
                self.state = 12
                self.expr()
                self.state = 17
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExprContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def inExpr(self):
            return self.getTypedRuleContext(DQLParser.InExprContext, 0)

        def orExpr(self):
            return self.getTypedRuleContext(DQLParser.OrExprContext, 0)

        def equalExpr(self):
            return self.getTypedRuleContext(DQLParser.EqualExprContext, 0)

        def getRuleIndex(self):
            return DQLParser.RULE_expr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterExpr'):
                listener.enterExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitExpr'):
                listener.exitExpr(self)

    def expr(self):

        localctx = DQLParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expr)
        try:
            self.state = 21
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 1, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self.inExpr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 19
                self.orExpr()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 20
                self.equalExpr()
                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class InExprContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(DQLParser.ID, 0)

        def COLON(self):
            return self.getToken(DQLParser.COLON, 0)

        def OPEN_PARENTHESES(self):
            return self.getToken(DQLParser.OPEN_PARENTHESES, 0)

        def CLOSE_PARENTHESES(self):
            return self.getToken(DQLParser.CLOSE_PARENTHESES, 0)

        def value(self, i: int=None):
            if i is None:
                return self.getTypedRuleContexts(DQLParser.ValueContext)
            else:
                return self.getTypedRuleContext(DQLParser.ValueContext, i)

        def getRuleIndex(self):
            return DQLParser.RULE_inExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterInExpr'):
                listener.enterInExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitInExpr'):
                listener.exitInExpr(self)

    def inExpr(self):

        localctx = DQLParser.InExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_inExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 23
            self.match(DQLParser.ID)
            self.state = 24
            self.match(DQLParser.COLON)
            self.state = 25
            self.match(DQLParser.OPEN_PARENTHESES)
            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & (
                (1 << DQLParser.INTEGER) | (1 << DQLParser.FLOAT) |
                (1 << DQLParser.STRING))) != 0):
                self.state = 26
                self.value()
                self.state = 31
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 32
            self.match(DQLParser.CLOSE_PARENTHESES)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OrExprContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(DQLParser.ID, 0)

        def COLON(self):
            return self.getToken(DQLParser.COLON, 0)

        def OPEN_CURLY(self):
            return self.getToken(DQLParser.OPEN_CURLY, 0)

        def CLOSE_CURLY(self):
            return self.getToken(DQLParser.CLOSE_CURLY, 0)

        def value(self, i: int=None):
            if i is None:
                return self.getTypedRuleContexts(DQLParser.ValueContext)
            else:
                return self.getTypedRuleContext(DQLParser.ValueContext, i)

        def getRuleIndex(self):
            return DQLParser.RULE_orExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterOrExpr'):
                listener.enterOrExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitOrExpr'):
                listener.exitOrExpr(self)

    def orExpr(self):

        localctx = DQLParser.OrExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_orExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            self.match(DQLParser.ID)
            self.state = 35
            self.match(DQLParser.COLON)
            self.state = 36
            self.match(DQLParser.OPEN_CURLY)
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & (
                (1 << DQLParser.INTEGER) | (1 << DQLParser.FLOAT) |
                (1 << DQLParser.STRING))) != 0):
                self.state = 37
                self.value()
                self.state = 42
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 43
            self.match(DQLParser.CLOSE_CURLY)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class EqualExprContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KEYWORD(self):
            return self.getToken(DQLParser.KEYWORD, 0)

        def COLON(self):
            return self.getToken(DQLParser.COLON, 0)

        def ID(self):
            return self.getToken(DQLParser.ID, 0)

        def value(self):
            return self.getTypedRuleContext(DQLParser.ValueContext, 0)

        def getRuleIndex(self):
            return DQLParser.RULE_equalExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterEqualExpr'):
                listener.enterEqualExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitEqualExpr'):
                listener.exitEqualExpr(self)

    def equalExpr(self):

        localctx = DQLParser.EqualExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_equalExpr)
        try:
            self.state = 51
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [DQLParser.KEYWORD]:
                self.enterOuterAlt(localctx, 1)
                self.state = 45
                self.match(DQLParser.KEYWORD)
                self.state = 46
                self.match(DQLParser.COLON)
                self.state = 47
                self.match(DQLParser.ID)
                pass
            elif token in [DQLParser.ID]:
                self.enterOuterAlt(localctx, 2)
                self.state = 48
                self.match(DQLParser.ID)
                self.state = 49
                self.match(DQLParser.COLON)
                self.state = 50
                self.value()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueContext(ParserRuleContext):
        def __init__(self,
                     parser,
                     parent: ParserRuleContext=None,
                     invokingState: int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER(self):
            return self.getToken(DQLParser.INTEGER, 0)

        def FLOAT(self):
            return self.getToken(DQLParser.FLOAT, 0)

        def STRING(self):
            return self.getToken(DQLParser.STRING, 0)

        def getRuleIndex(self):
            return DQLParser.RULE_value

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'enterValue'):
                listener.enterValue(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, 'exitValue'):
                listener.exitValue(self)

    def value(self):

        localctx = DQLParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_value)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            _la = self._input.LA(1)
            if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & (
                (1 << DQLParser.INTEGER) | (1 << DQLParser.FLOAT) |
                (1 << DQLParser.STRING))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
