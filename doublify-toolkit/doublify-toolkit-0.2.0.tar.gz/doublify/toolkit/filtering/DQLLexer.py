# Generated from DQL.g4 by ANTLR 4.6
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write('\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2\r')
        buf.write('R\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7')
        buf.write('\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\3\2\3\2\3\3')
        buf.write('\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\7\3\7\3\7\5\7)')
        buf.write('\n\7\3\b\6\b,\n\b\r\b\16\b-\3\t\7\t\61\n\t\f\t\16\t\64')
        buf.write('\13\t\3\t\3\t\6\t8\n\t\r\t\16\t9\3\n\3\n\7\n>\n\n\f\n')
        buf.write('\16\nA\13\n\3\n\3\n\3\13\3\13\7\13G\n\13\f\13\16\13J\13')
        buf.write('\13\3\f\6\fM\n\f\r\f\16\fN\3\f\3\f\2\2\r\3\3\5\4\7\5\t')
        buf.write('\6\13\7\r\b\17\t\21\n\23\13\25\f\27\r\3\2\7\3\2\62;\4')
        buf.write("\2$$>>\5\2C\\aac|\6\2\62;C\\aac|\5\2\13\f\16\17\"\"X\2")
        buf.write('\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3')
        buf.write('\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2')
        buf.write('\2\2\2\25\3\2\2\2\2\27\3\2\2\2\3\31\3\2\2\2\5\33\3\2\2')
        buf.write('\2\7\35\3\2\2\2\t\37\3\2\2\2\13!\3\2\2\2\r(\3\2\2\2\17')
        buf.write('+\3\2\2\2\21\62\3\2\2\2\23;\3\2\2\2\25D\3\2\2\2\27L\3')
        buf.write('\2\2\2\31\32\7*\2\2\32\4\3\2\2\2\33\34\7+\2\2\34\6\3\2')
        buf.write('\2\2\35\36\7}\2\2\36\b\3\2\2\2\37 \7\177\2\2 \n\3\2\2')
        buf.write("\2!\"\7<\2\2\"\f\3\2\2\2#$\7k\2\2$)\7u\2\2%&\7p\2\2&\'")
        buf.write("\7q\2\2\')\7v\2\2(#\3\2\2\2(%\3\2\2\2)\16\3\2\2\2*,\t")
        buf.write('\2\2\2+*\3\2\2\2,-\3\2\2\2-+\3\2\2\2-.\3\2\2\2.\20\3\2')
        buf.write('\2\2/\61\t\2\2\2\60/\3\2\2\2\61\64\3\2\2\2\62\60\3\2\2')
        buf.write('\2\62\63\3\2\2\2\63\65\3\2\2\2\64\62\3\2\2\2\65\67\7\60')
        buf.write('\2\2\668\t\2\2\2\67\66\3\2\2\289\3\2\2\29\67\3\2\2\29')
        buf.write(':\3\2\2\2:\22\3\2\2\2;?\7$\2\2<>\n\3\2\2=<\3\2\2\2>A\3')
        buf.write('\2\2\2?=\3\2\2\2?@\3\2\2\2@B\3\2\2\2A?\3\2\2\2BC\7$\2')
        buf.write('\2C\24\3\2\2\2DH\t\4\2\2EG\t\5\2\2FE\3\2\2\2GJ\3\2\2\2')
        buf.write('HF\3\2\2\2HI\3\2\2\2I\26\3\2\2\2JH\3\2\2\2KM\t\6\2\2L')
        buf.write('K\3\2\2\2MN\3\2\2\2NL\3\2\2\2NO\3\2\2\2OP\3\2\2\2PQ\b')
        buf.write('\f\2\2Q\30\3\2\2\2\n\2(-\629?HN\3\b\2\2')
        return buf.getvalue()


class DQLLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

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

    modeNames = ['DEFAULT_MODE']

    literalNames = ['<INVALID>', "'('", "')'", "'{'", "'}'", "':'"]

    symbolicNames = [
        '<INVALID>', 'OPEN_PARENTHESES', 'CLOSE_PARENTHESES', 'OPEN_CURLY',
        'CLOSE_CURLY', 'COLON', 'KEYWORD', 'INTEGER', 'FLOAT', 'STRING', 'ID',
        'WS'
    ]

    ruleNames = [
        'OPEN_PARENTHESES', 'CLOSE_PARENTHESES', 'OPEN_CURLY', 'CLOSE_CURLY',
        'COLON', 'KEYWORD', 'INTEGER', 'FLOAT', 'STRING', 'ID', 'WS'
    ]

    grammarFileName = 'DQL.g4'

    def __init__(self, input=None):
        super().__init__(input)
        self.checkVersion('4.6')
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA,
                                         PredictionContextCache())
        self._actions = None
        self._predicates = None
