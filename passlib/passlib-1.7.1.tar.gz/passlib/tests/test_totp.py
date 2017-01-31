"""passlib.tests -- test passlib.totp"""
#=============================================================================
# imports
#=============================================================================
# core
import datetime
from functools import partial
import logging; log = logging.getLogger(__name__)
import sys
import time as _time
# site
# pkg
from passlib import exc
from passlib.utils.compat import unicode, u
from passlib.tests.utils import TestCase, time_call
# subject
from passlib import totp as totp_module
from passlib.totp import TOTP, AppWallet, AES_SUPPORT
# local
__all__ = [
    "EngineTest",
]

#=============================================================================
# helpers
#=============================================================================

# XXX: python 3 changed what error base64.b16decode() throws, from TypeError to base64.Error().
#      it wasn't until 3.3 that base32decode() also got changed.
#      really should normalize this in the code to a single BinaryDecodeError,
#      predicting this cross-version is getting unmanagable.
Base32DecodeError = Base16DecodeError = TypeError
if sys.version_info >= (3,0):
    from binascii import Error as Base16DecodeError
if sys.version_info >= (3,3):
    from binascii import Error as Base32DecodeError

PASS1 = "abcdef"
PASS2 = b"\x00\xFF"
KEY1 = '4AOGGDBBQSYHNTUZ'
KEY1_RAW = b'\xe0\x1cc\x0c!\x84\xb0v\xce\x99'
KEY2_RAW = b'\xee]\xcb9\x870\x06 D\xc8y/\xa54&\xe4\x9c\x13\xc2\x18'
KEY3 = 'S3JDVB7QD2R7JPXX' # used in docstrings
KEY4 = 'JBSWY3DPEHPK3PXP' # from google keyuri spec
KEY4_RAW = b'Hello!\xde\xad\xbe\xef'

# NOTE: for randtime() below,
#       * want at least 7 bits on fractional side, to test fractional times to at least 0.01s precision
#       * want at least 32 bits on integer side, to test for 32-bit epoch issues.
#       most systems *should* have 53 bit mantissa, leaving plenty of room on both ends,
#       so using (1<<37) as scale, to allocate 16 bits on fractional side, but generate reasonable # of > 1<<32 times.
#       sanity check that we're above 44 ensures minimum requirements (44 - 37 int = 7 frac)
assert sys.float_info.radix == 2, "unexpected float_info.radix"
assert sys.float_info.mant_dig >= 44, "double precision unexpectedly small"

def _get_max_time_t():
    """
    helper to calc max_time_t constant (see below)
    """
    value = 1 << 30  # even for 32 bit systems will handle this
    year = 0
    while True:
        next_value = value << 1
        try:
            next_year = datetime.datetime.utcfromtimestamp(next_value-1).year
        except (ValueError, OSError, OverflowError):
            # utcfromtimestamp() may throw any of the following:
            #
            # * year out of range for datetime:
            #   py < 3.6 throws ValueError.
            #   (py 3.6.0 returns odd value instead, see workaround below)
            #
            # * int out of range for host's gmtime/localtime:
            #   py2 throws ValueError, py3 throws OSError.
            #
            # * int out of range for host's time_t:
            #   py2 throws ValueError, py3 throws OverflowError.
            #
            break

        # Workaround for python 3.6.0 issue --
        # Instead of throwing ValueError if year out of range for datetime,
        # Python 3.6 will do some weird behavior that masks high bits
        # e.g. (1<<40) -> year 36812, but (1<<41) -> year 6118.
        # (Appears to be bug http://bugs.python.org/issue29100)
        # This check stops at largest non-wrapping bit size.
        if next_year < year:
            break

        value = next_value

    # 'value-1' is maximum.
    value -= 1

    # check for crazy case where we're beyond what datetime supports
    # (caused by bug 29100 again). compare to max value that datetime
    # module supports -- datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
    max_datetime_timestamp = 253402318800
    return min(value, max_datetime_timestamp)

#: Rough approximation of max value acceptable by hosts's time_t.
#: This is frequently ~2**37 on 64 bit, and ~2**31 on 32 bit systems.
max_time_t = _get_max_time_t()

def to_b32_size(raw_size):
    return (raw_size * 8 + 4) // 5

#=============================================================================
# wallet
#=============================================================================
class AppWalletTest(TestCase):
    descriptionPrefix = "passlib.totp.AppWallet"

    #=============================================================================
    # constructor
    #=============================================================================

    def test_secrets_types(self):
        """constructor -- 'secrets' param -- input types"""

        # no secrets
        wallet = AppWallet()
        self.assertEqual(wallet._secrets, {})
        self.assertFalse(wallet.has_secrets)

        # dict
        ref = {"1": b"aaa", "2": b"bbb"}
        wallet = AppWallet(ref)
        self.assertEqual(wallet._secrets, ref)
        self.assertTrue(wallet.has_secrets)

        # # list
        # wallet = AppWallet(list(ref.items()))
        # self.assertEqual(wallet._secrets, ref)

        # # iter
        # wallet = AppWallet(iter(ref.items()))
        # self.assertEqual(wallet._secrets, ref)

        # "tag:value" string
        wallet = AppWallet("\n 1: aaa\n# comment\n \n2: bbb   ")
        self.assertEqual(wallet._secrets, ref)

        # ensure ":" allowed in secret
        wallet = AppWallet("1: aaa: bbb \n# comment\n \n2: bbb   ")
        self.assertEqual(wallet._secrets, {"1": b"aaa: bbb", "2": b"bbb"})

        # json dict
        wallet = AppWallet('{"1":"aaa","2":"bbb"}')
        self.assertEqual(wallet._secrets, ref)

        # # json list
        # wallet = AppWallet('[["1","aaa"],["2","bbb"]]')
        # self.assertEqual(wallet._secrets, ref)

        # invalid type
        self.assertRaises(TypeError, AppWallet, 123)

        # invalid json obj
        self.assertRaises(TypeError, AppWallet, "[123]")

        # # invalid list items
        # self.assertRaises(ValueError, AppWallet, ["1", b"aaa"])

        # forbid empty secret
        self.assertRaises(ValueError, AppWallet, {"1": "aaa", "2": ""})

    def test_secrets_tags(self):
        """constructor -- 'secrets' param -- tag/value normalization"""

        # test reference
        ref = {"1": b"aaa", "02": b"bbb", "C": b"ccc"}
        wallet = AppWallet(ref)
        self.assertEqual(wallet._secrets, ref)

        # accept unicode
        wallet = AppWallet({u("1"): b"aaa", u("02"): b"bbb", u("C"): b"ccc"})
        self.assertEqual(wallet._secrets, ref)

        # normalize int tags
        wallet = AppWallet({1: b"aaa", "02": b"bbb", "C": b"ccc"})
        self.assertEqual(wallet._secrets, ref)

        # forbid non-str/int tags
        self.assertRaises(TypeError, AppWallet, {(1,): "aaa"})

        # accept valid tags
        wallet = AppWallet({"1-2_3.4": b"aaa"})

        # forbid invalid tags
        self.assertRaises(ValueError, AppWallet, {"-abc": "aaa"})
        self.assertRaises(ValueError, AppWallet, {"ab*$": "aaa"})

        # coerce value to bytes
        wallet = AppWallet({"1": u("aaa"), "02": "bbb", "C": b"ccc"})
        self.assertEqual(wallet._secrets, ref)

        # forbid invalid value types
        self.assertRaises(TypeError, AppWallet, {"1": 123})
        self.assertRaises(TypeError, AppWallet, {"1": None})
        self.assertRaises(TypeError, AppWallet, {"1": []})

    # TODO: test secrets_path

    def test_default_tag(self):
        """constructor -- 'default_tag' param"""

        # should sort numerically
        wallet = AppWallet({"1": "one", "02": "two"})
        self.assertEqual(wallet.default_tag, "02")
        self.assertEqual(wallet.get_secret(wallet.default_tag), b"two")

        # should sort alphabetically if non-digit present
        wallet = AppWallet({"1": "one", "02": "two", "A": "aaa"})
        self.assertEqual(wallet.default_tag, "A")
        self.assertEqual(wallet.get_secret(wallet.default_tag), b"aaa")

        # should use honor custom tag
        wallet = AppWallet({"1": "one", "02": "two", "A": "aaa"}, default_tag="1")
        self.assertEqual(wallet.default_tag, "1")
        self.assertEqual(wallet.get_secret(wallet.default_tag), b"one")

        # throw error on unknown value
        self.assertRaises(KeyError, AppWallet, {"1": "one", "02": "two", "A": "aaa"},
                          default_tag="B")

        # should be empty
        wallet = AppWallet()
        self.assertEqual(wallet.default_tag, None)
        self.assertRaises(KeyError, wallet.get_secret, None)

    # TODO: test 'cost' param

    #=============================================================================
    # encrypt_key() & decrypt_key() helpers
    #=============================================================================
    def require_aes_support(self, canary=None):
        if AES_SUPPORT:
            canary and canary()
        else:
            canary and self.assertRaises(RuntimeError, canary)
            raise self.skipTest("'cryptography' package not installed")

    def test_decrypt_key(self):
        """.decrypt_key()"""

        wallet = AppWallet({"1": PASS1, "2": PASS2})

        # check for support
        CIPHER1 = dict(v=1, c=13, s='6D7N7W53O7HHS37NLUFQ',
                       k='MHCTEGSNPFN5CGBJ', t='1')
        self.require_aes_support(canary=partial(wallet.decrypt_key, CIPHER1))

        # reference key
        self.assertEqual(wallet.decrypt_key(CIPHER1)[0], KEY1_RAW)

        # different salt used to encrypt same raw key
        CIPHER2 = dict(v=1, c=13, s='SPZJ54Y6IPUD2BYA4C6A',
                       k='ZGDXXTVQOWYLC2AU', t='1')
        self.assertEqual(wallet.decrypt_key(CIPHER2)[0], KEY1_RAW)

        # different sized key, password, and cost
        CIPHER3 = dict(v=1, c=8, s='FCCTARTIJWE7CPQHUDKA',
                       k='D2DRS32YESGHHINWFFCELKN7Z6NAHM4M', t='2')
        self.assertEqual(wallet.decrypt_key(CIPHER3)[0], KEY2_RAW)

        # wrong password should silently result in wrong key
        temp = CIPHER1.copy()
        temp.update(t='2')
        self.assertEqual(wallet.decrypt_key(temp)[0], b'\xafD6.F7\xeb\x19\x05Q')

        # missing tag should throw error
        temp = CIPHER1.copy()
        temp.update(t='3')
        self.assertRaises(KeyError, wallet.decrypt_key, temp)

        # unknown version should throw error
        temp = CIPHER1.copy()
        temp.update(v=999)
        self.assertRaises(ValueError, wallet.decrypt_key, temp)

    def test_decrypt_key_needs_recrypt(self):
        """.decrypt_key() -- needs_recrypt flag"""
        self.require_aes_support()

        wallet = AppWallet({"1": PASS1, "2": PASS2}, encrypt_cost=13)

        # ref should be accepted
        ref = dict(v=1, c=13, s='AAAA', k='AAAA', t='2')
        self.assertFalse(wallet.decrypt_key(ref)[1])

        # wrong cost
        temp = ref.copy()
        temp.update(c=8)
        self.assertTrue(wallet.decrypt_key(temp)[1])

        # wrong tag
        temp = ref.copy()
        temp.update(t="1")
        self.assertTrue(wallet.decrypt_key(temp)[1])

        # XXX: should this check salt_size?

    def assertSaneResult(self, result, wallet, key, tag="1",
                         needs_recrypt=False):
        """check encrypt_key() result has expected format"""

        self.assertEqual(set(result), set(["v", "t", "c", "s", "k"]))

        self.assertEqual(result['v'], 1)
        self.assertEqual(result['t'], tag)
        self.assertEqual(result['c'], wallet.encrypt_cost)

        self.assertEqual(len(result['s']), to_b32_size(wallet.salt_size))
        self.assertEqual(len(result['k']), to_b32_size(len(key)))

        result_key, result_needs_recrypt = wallet.decrypt_key(result)
        self.assertEqual(result_key, key)
        self.assertEqual(result_needs_recrypt, needs_recrypt)

    def test_encrypt_key(self):
        """.encrypt_key()"""

        # check for support
        wallet = AppWallet({"1": PASS1}, encrypt_cost=5)
        self.require_aes_support(canary=partial(wallet.encrypt_key, KEY1_RAW))

        # basic behavior
        result = wallet.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet, KEY1_RAW)

        # creates new salt each time
        other = wallet.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet, KEY1_RAW)
        self.assertNotEqual(other['s'], result['s'])
        self.assertNotEqual(other['k'], result['k'])

        # honors custom cost
        wallet2 = AppWallet({"1": PASS1}, encrypt_cost=6)
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW)

        # honors default tag
        wallet2 = AppWallet({"1": PASS1, "2": PASS2})
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW, tag="2")

        # honor salt size
        wallet2 = AppWallet({"1": PASS1})
        wallet2.salt_size = 64
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW)

        # larger key
        result = wallet.encrypt_key(KEY2_RAW)
        self.assertSaneResult(result, wallet, KEY2_RAW)

        # border case: empty key
        # XXX: might want to allow this, but documenting behavior for now
        self.assertRaises(ValueError, wallet.encrypt_key, b"")

    def test_encrypt_cost_timing(self):
        """verify cost parameter via timing"""
        self.require_aes_support()

        # time default cost
        wallet = AppWallet({"1": "aaa"})
        wallet.encrypt_cost -= 2
        delta, _ = time_call(partial(wallet.encrypt_key, KEY1_RAW), maxtime=0)

        # this should take (2**3=8) times as long
        wallet.encrypt_cost += 3
        delta2, _ = time_call(partial(wallet.encrypt_key, KEY1_RAW), maxtime=0)

        self.assertAlmostEqual(delta2, delta*8, delta=(delta*8)*0.5)

    #=============================================================================
    # eoc
    #=============================================================================

#=============================================================================
# common OTP code
#=============================================================================

#: used as base value for RFC test vector keys
RFC_KEY_BYTES_20 = "12345678901234567890".encode("ascii")
RFC_KEY_BYTES_32 = (RFC_KEY_BYTES_20*2)[:32]
RFC_KEY_BYTES_64 = (RFC_KEY_BYTES_20*4)[:64]

# TODO: this class is separate from TotpTest due to historical issue,
#       when there was a base class, and a separate HOTP class.
#       these test case classes should probably be combined.
class TotpTest(TestCase):
    """
    common code shared by TotpTest & HotpTest
    """
    #=============================================================================
    # class attrs
    #=============================================================================

    descriptionPrefix = "passlib.totp.TOTP"

    #=============================================================================
    # setup
    #=============================================================================
    def setUp(self):
        super(TotpTest, self).setUp()

        # clear norm_hash_name() cache so 'unknown hash' warnings get emitted each time
        from passlib.crypto.digest import lookup_hash
        lookup_hash.clear_cache()

        # monkeypatch module's rng to be deterministic
        self.patchAttr(totp_module, "rng", self.getRandom())

    #=============================================================================
    # general helpers
    #=============================================================================
    def randtime(self):
        """
        helper to generate random epoch time
        :returns float: epoch time
        """
        return self.getRandom().random() * max_time_t

    def randotp(self, cls=None, **kwds):
        """
        helper which generates a random TOTP instance.
        """
        rng = self.getRandom()
        if "key" not in kwds:
            kwds['new'] = True
        kwds.setdefault("digits", rng.randint(6, 10))
        kwds.setdefault("alg", rng.choice(["sha1", "sha256", "sha512"]))
        kwds.setdefault("period", rng.randint(10, 120))
        return (cls or TOTP)(**kwds)

    def test_randotp(self):
        """
        internal test -- randotp()
        """
        otp1 = self.randotp()
        otp2 = self.randotp()

        self.assertNotEqual(otp1.key, otp2.key, "key not randomized:")

        # NOTE: has (1/5)**10 odds of failure
        for _ in range(10):
            if otp1.digits != otp2.digits:
                break
            otp2 = self.randotp()
        else:
            self.fail("digits not randomized")

        # NOTE: has (1/3)**10 odds of failure
        for _ in range(10):
            if otp1.alg != otp2.alg:
                break
            otp2 = self.randotp()
        else:
            self.fail("alg not randomized")

    #=============================================================================
    # reference vector helpers
    #=============================================================================

    #: default options used by test vectors (unless otherwise stated)
    vector_defaults = dict(format="base32", alg="sha1", period=30, digits=8)

    #: various TOTP test vectors,
    #: each element in list has format [options, (time, token <, int(expires)>), ...]
    vectors = [

        #-------------------------------------------------------------------------
        # passlib test vectors
        #-------------------------------------------------------------------------

        # 10 byte key, 6 digits
        [dict(key="ACDEFGHJKL234567", digits=6),
            # test fencepost to make sure we're rounding right
            (1412873399, '221105'), # == 29 mod 30
            (1412873400, '178491'), # == 0 mod 30
            (1412873401, '178491'), # == 1 mod 30
            (1412873429, '178491'), # == 29 mod 30
            (1412873430, '915114'), # == 0 mod 30
        ],

        # 10 byte key, 8 digits
        [dict(key="ACDEFGHJKL234567", digits=8),
            # should be same as 6 digits (above), but w/ 2 more digits on left side of token.
            (1412873399, '20221105'), # == 29 mod 30
            (1412873400, '86178491'), # == 0 mod 30
            (1412873401, '86178491'), # == 1 mod 30
            (1412873429, '86178491'), # == 29 mod 30
            (1412873430, '03915114'), # == 0 mod 30
        ],

        # sanity check on key used in docstrings
        [dict(key="S3JD-VB7Q-D2R7-JPXX", digits=6),
            (1419622709, '000492'),
            (1419622739, '897212'),
        ],

        #-------------------------------------------------------------------------
        # reference vectors taken from http://tools.ietf.org/html/rfc6238, appendix B
        # NOTE: while appendix B states same key used for all tests, the reference
        #       code in the appendix repeats the key up to the alg's block size,
        #       and uses *that* as the secret... so that's what we're doing here.
        #-------------------------------------------------------------------------

        # sha1 test vectors
        [dict(key=RFC_KEY_BYTES_20, format="raw", alg="sha1"),
            (59, '94287082'),
            (1111111109, '07081804'),
            (1111111111, '14050471'),
            (1234567890, '89005924'),
            (2000000000, '69279037'),
            (20000000000, '65353130'),
        ],

        # sha256 test vectors
        [dict(key=RFC_KEY_BYTES_32, format="raw", alg="sha256"),
            (59, '46119246'),
            (1111111109, '68084774'),
            (1111111111, '67062674'),
            (1234567890, '91819424'),
            (2000000000, '90698825'),
            (20000000000, '77737706'),
        ],

        # sha512 test vectors
        [dict(key=RFC_KEY_BYTES_64, format="raw", alg="sha512"),
            (59, '90693936'),
            (1111111109, '25091201'),
            (1111111111, '99943326'),
            (1234567890, '93441116'),
            (2000000000, '38618901'),
            (20000000000, '47863826'),
        ],

        #-------------------------------------------------------------------------
        # other test vectors
        #-------------------------------------------------------------------------

        # generated at http://blog.tinisles.com/2011/10/google-authenticator-one-time-password-algorithm-in-javascript
        [dict(key="JBSWY3DPEHPK3PXP", digits=6), (1409192430, '727248'), (1419890990, '122419')],
        [dict(key="JBSWY3DPEHPK3PXP", digits=9, period=41), (1419891152, '662331049')],

        # found in https://github.com/eloquent/otis/blob/develop/test/suite/Totp/Value/TotpValueGeneratorTest.php, line 45
        [dict(key=RFC_KEY_BYTES_20, format="raw", period=60), (1111111111, '19360094')],
        [dict(key=RFC_KEY_BYTES_32, format="raw", alg="sha256", period=60), (1111111111, '40857319')],
        [dict(key=RFC_KEY_BYTES_64, format="raw", alg="sha512", period=60), (1111111111, '37023009')],

    ]

    def iter_test_vectors(self):
        """
        helper to iterate over test vectors.
        yields ``(totp, time, token, expires, prefix)`` tuples.
        """
        from passlib.totp import TOTP
        for row in self.vectors:
            kwds = self.vector_defaults.copy()
            kwds.update(row[0])
            for entry in row[1:]:
                if len(entry) == 3:
                    time, token, expires = entry
                else:
                    time, token = entry
                    expires = None
                # NOTE: not re-using otp between calls so that stateful methods
                #       (like .match) don't have problems.
                log.debug("test vector: %r time=%r token=%r expires=%r", kwds, time, token, expires)
                otp = TOTP(**kwds)
                prefix = "alg=%r time=%r token=%r: " % (otp.alg, time, token)
                yield otp, time, token, expires, prefix

    #=============================================================================
    # constructor tests
    #=============================================================================
    def test_ctor_w_new(self):
        """constructor -- 'new'  parameter"""

        # exactly one of 'key' or 'new' is required
        self.assertRaises(TypeError, TOTP)
        self.assertRaises(TypeError, TOTP, key='4aoggdbbqsyhntuz', new=True)

        # generates new key
        otp = TOTP(new=True)
        otp2 = TOTP(new=True)
        self.assertNotEqual(otp.key, otp2.key)

    def test_ctor_w_size(self):
        """constructor -- 'size'  parameter"""

        # should default to digest size, per RFC
        self.assertEqual(len(TOTP(new=True, alg="sha1").key), 20)
        self.assertEqual(len(TOTP(new=True, alg="sha256").key), 32)
        self.assertEqual(len(TOTP(new=True, alg="sha512").key), 64)

        # explicit key size
        self.assertEqual(len(TOTP(new=True, size=10).key), 10)
        self.assertEqual(len(TOTP(new=True, size=16).key), 16)

        # for new=True, maximum size enforced (based on alg)
        self.assertRaises(ValueError, TOTP, new=True, size=21, alg="sha1")

        # for new=True, minimum size enforced
        self.assertRaises(ValueError, TOTP, new=True, size=9)

        # for existing key, minimum size is only warned about
        with self.assertWarningList([
                dict(category=exc.PasslibSecurityWarning, message_re=".*for security purposes, secret key must be.*")
                ]):
            _ = TOTP('0A'*9, 'hex')

    def test_ctor_w_key_and_format(self):
        """constructor -- 'key' and 'format' parameters"""

        # handle base32 encoding (the default)
        self.assertEqual(TOTP(KEY1).key, KEY1_RAW)

            # .. w/ lower case
        self.assertEqual(TOTP(KEY1.lower()).key, KEY1_RAW)

            # .. w/ spaces (e.g. user-entered data)
        self.assertEqual(TOTP(' 4aog gdbb qsyh ntuz ').key, KEY1_RAW)

            # .. w/ invalid char
        self.assertRaises(Base32DecodeError, TOTP, 'ao!ggdbbqsyhntuz')

        # handle hex encoding
        self.assertEqual(TOTP('e01c630c2184b076ce99', 'hex').key, KEY1_RAW)

            # .. w/ invalid char
        self.assertRaises(Base16DecodeError, TOTP, 'X01c630c2184b076ce99', 'hex')

        # handle raw bytes
        self.assertEqual(TOTP(KEY1_RAW, "raw").key, KEY1_RAW)

    def test_ctor_w_alg(self):
        """constructor -- 'alg' parameter"""

        # normalize hash names
        self.assertEqual(TOTP(KEY1, alg="SHA-256").alg, "sha256")
        self.assertEqual(TOTP(KEY1, alg="SHA256").alg, "sha256")

        # invalid alg
        self.assertRaises(ValueError, TOTP, KEY1, alg="SHA-333")

    def test_ctor_w_digits(self):
        """constructor -- 'digits' parameter"""
        self.assertRaises(ValueError, TOTP, KEY1, digits=5)
        self.assertEqual(TOTP(KEY1, digits=6).digits, 6)  # min value
        self.assertEqual(TOTP(KEY1, digits=10).digits, 10)  # max value
        self.assertRaises(ValueError, TOTP, KEY1, digits=11)

    def test_ctor_w_period(self):
        """constructor -- 'period' parameter"""

        # default
        self.assertEqual(TOTP(KEY1).period, 30)

        # explicit value
        self.assertEqual(TOTP(KEY1, period=63).period, 63)

        # reject wrong type
        self.assertRaises(TypeError, TOTP, KEY1, period=1.5)
        self.assertRaises(TypeError, TOTP, KEY1, period='abc')

        # reject non-positive values
        self.assertRaises(ValueError, TOTP, KEY1, period=0)
        self.assertRaises(ValueError, TOTP, KEY1, period=-1)

    def test_ctor_w_label(self):
        """constructor -- 'label' parameter"""
        self.assertEqual(TOTP(KEY1).label, None)
        self.assertEqual(TOTP(KEY1, label="foo@bar").label, "foo@bar")
        self.assertRaises(ValueError, TOTP, KEY1, label="foo:bar")

    def test_ctor_w_issuer(self):
        """constructor -- 'issuer' parameter"""
        self.assertEqual(TOTP(KEY1).issuer, None)
        self.assertEqual(TOTP(KEY1, issuer="foo.com").issuer, "foo.com")
        self.assertRaises(ValueError, TOTP, KEY1, issuer="foo.com:bar")

    #=============================================================================
    # using() tests
    #=============================================================================

    # TODO: test using() w/ 'digits', 'alg', 'issue', 'wallet', **wallet_kwds

    def test_using_w_period(self):
        """using() -- 'period' parameter"""

        # default
        self.assertEqual(TOTP(KEY1).period, 30)

        # explicit value
        self.assertEqual(TOTP.using(period=63)(KEY1).period, 63)

        # reject wrong type
        self.assertRaises(TypeError, TOTP.using, period=1.5)
        self.assertRaises(TypeError, TOTP.using, period='abc')

        # reject non-positive values
        self.assertRaises(ValueError, TOTP.using, period=0)
        self.assertRaises(ValueError, TOTP.using, period=-1)

    def test_using_w_now(self):
        """using -- 'now' parameter"""

        # NOTE: reading time w/ normalize_time() to make sure custom .now actually has effect.

        # default -- time.time
        otp = self.randotp()
        self.assertIs(otp.now, _time.time)
        self.assertAlmostEqual(otp.normalize_time(None), int(_time.time()))

        # custom function
        counter = [123.12]
        def now():
            counter[0] += 1
            return counter[0]
        otp = self.randotp(cls=TOTP.using(now=now))
        # NOTE: TOTP() constructor invokes this as part of test, using up counter values 124 & 125
        self.assertEqual(otp.normalize_time(None), 126)
        self.assertEqual(otp.normalize_time(None), 127)

        # require callable
        self.assertRaises(TypeError, TOTP.using, now=123)

        # require returns int/float
        msg_re = r"now\(\) function must return non-negative"
        self.assertRaisesRegex(AssertionError, msg_re, TOTP.using, now=lambda: 'abc')

        # require returns non-negative value
        self.assertRaisesRegex(AssertionError, msg_re, TOTP.using, now=lambda: -1)

    #=============================================================================
    # internal method tests
    #=============================================================================

    def test_normalize_token_instance(self, otp=None):
        """normalize_token() -- instance method"""
        if otp is None:
            otp = self.randotp(digits=7)

        # unicode & bytes
        self.assertEqual(otp.normalize_token(u('1234567')), '1234567')
        self.assertEqual(otp.normalize_token(b'1234567'), '1234567')

        # int
        self.assertEqual(otp.normalize_token(1234567), '1234567')

        # int which needs 0 padding
        self.assertEqual(otp.normalize_token(234567), '0234567')

        # reject wrong types (float, None)
        self.assertRaises(TypeError, otp.normalize_token, 1234567.0)
        self.assertRaises(TypeError, otp.normalize_token, None)

        # too few digits
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, '123456')

        # too many digits
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, '01234567')
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, 12345678)

    def test_normalize_token_class(self):
        """normalize_token() -- class method"""
        self.test_normalize_token_instance(otp=TOTP.using(digits=7))

    def test_normalize_time(self):
        """normalize_time()"""
        TotpFactory = TOTP.using()
        otp = self.randotp(TotpFactory)

        for _ in range(10):
            time = self.randtime()
            tint = int(time)

            self.assertEqual(otp.normalize_time(time), tint)
            self.assertEqual(otp.normalize_time(tint + 0.5), tint)

            self.assertEqual(otp.normalize_time(tint), tint)

            dt = datetime.datetime.utcfromtimestamp(time)
            self.assertEqual(otp.normalize_time(dt), tint)

            orig = TotpFactory.now
            try:
                TotpFactory.now = staticmethod(lambda: time)
                self.assertEqual(otp.normalize_time(None), tint)
            finally:
                TotpFactory.now = orig

        self.assertRaises(TypeError, otp.normalize_time, '1234')

    #=============================================================================
    # key attr tests
    #=============================================================================

    def test_key_attrs(self):
        """pretty_key() and .key attributes"""
        rng = self.getRandom()

        # test key attrs
        otp = TOTP(KEY1_RAW, "raw")
        self.assertEqual(otp.key, KEY1_RAW)
        self.assertEqual(otp.hex_key, 'e01c630c2184b076ce99')
        self.assertEqual(otp.base32_key, KEY1)

        # test pretty_key()
        self.assertEqual(otp.pretty_key(), '4AOG-GDBB-QSYH-NTUZ')
        self.assertEqual(otp.pretty_key(sep=" "), '4AOG GDBB QSYH NTUZ')
        self.assertEqual(otp.pretty_key(sep=False), KEY1)
        self.assertEqual(otp.pretty_key(format="hex"), 'e01c-630c-2184-b076-ce99')

        # quick fuzz test: make attr access works for random key & random size
        otp = TOTP(new=True, size=rng.randint(10, 20))
        _ = otp.hex_key
        _ = otp.base32_key
        _ = otp.pretty_key()

    #=============================================================================
    # generate() tests
    #=============================================================================
    def test_totp_token(self):
        """generate() -- TotpToken() class"""
        from passlib.totp import TOTP, TotpToken

        # test known set of values
        otp = TOTP('s3jdvb7qd2r7jpxx')
        result = otp.generate(1419622739)
        self.assertIsInstance(result, TotpToken)
        self.assertEqual(result.token, '897212')
        self.assertEqual(result.counter, 47320757)
        ##self.assertEqual(result.start_time, 1419622710)
        self.assertEqual(result.expire_time, 1419622740)
        self.assertEqual(result, ('897212', 1419622740))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], '897212')
        self.assertEqual(result[1], 1419622740)
        self.assertRaises(IndexError, result.__getitem__, -3)
        self.assertRaises(IndexError, result.__getitem__, 2)
        self.assertTrue(result)

        # time dependant bits...
        otp.now = lambda : 1419622739.5
        self.assertEqual(result.remaining, 0.5)
        self.assertTrue(result.valid)

        otp.now = lambda : 1419622741
        self.assertEqual(result.remaining, 0)
        self.assertFalse(result.valid)

        # same time -- shouldn't return same object, but should be equal
        result2 = otp.generate(1419622739)
        self.assertIsNot(result2, result)
        self.assertEqual(result2, result)

        # diff time in period -- shouldn't return same object, but should be equal
        result3 = otp.generate(1419622711)
        self.assertIsNot(result3, result)
        self.assertEqual(result3, result)

        # shouldn't be equal
        result4 = otp.generate(1419622999)
        self.assertNotEqual(result4, result)

    def test_generate(self):
        """generate()"""
        from passlib.totp import TOTP

        # generate token
        otp = TOTP(new=True)
        time = self.randtime()
        result = otp.generate(time)
        token = result.token
        self.assertIsInstance(token, unicode)
        start_time = result.counter * 30

        # should generate same token for next 29s
        self.assertEqual(otp.generate(start_time + 29).token, token)

        # and new one at 30s
        self.assertNotEqual(otp.generate(start_time + 30).token, token)

        # verify round-trip conversion of datetime
        dt = datetime.datetime.utcfromtimestamp(time)
        self.assertEqual(int(otp.normalize_time(dt)), int(time))

        # handle datetime object
        self.assertEqual(otp.generate(dt).token, token)

        # omitting value should use current time
        otp2 = TOTP.using(now=lambda: time)(key=otp.base32_key)
        self.assertEqual(otp2.generate().token, token)

        # reject invalid time
        self.assertRaises(ValueError, otp.generate, -1)

    def test_generate_w_reference_vectors(self):
        """generate() -- reference vectors"""
        for otp, time, token, expires, prefix in self.iter_test_vectors():
            # should output correct token for specified time
            result = otp.generate(time)
            self.assertEqual(result.token, token, msg=prefix)
            self.assertEqual(result.counter, time // otp.period, msg=prefix)
            if expires:
                self.assertEqual(result.expire_time, expires)

    #=============================================================================
    # TotpMatch() tests
    #=============================================================================

    def assertTotpMatch(self, match, time, skipped=0, period=30, window=30, msg=''):
        from passlib.totp import TotpMatch

        # test type
        self.assertIsInstance(match, TotpMatch)

        # totp sanity check
        self.assertIsInstance(match.totp, TOTP)
        self.assertEqual(match.totp.period, period)

        # test attrs
        self.assertEqual(match.time, time, msg=msg + " matched time:")
        expected = time // period
        counter = expected + skipped
        self.assertEqual(match.counter, counter, msg=msg + " matched counter:")
        self.assertEqual(match.expected_counter, expected, msg=msg + " expected counter:")
        self.assertEqual(match.skipped, skipped, msg=msg + " skipped:")
        self.assertEqual(match.cache_seconds, period + window)
        expire_time = (counter + 1) * period
        self.assertEqual(match.expire_time, expire_time)
        self.assertEqual(match.cache_time, expire_time + window)

        # test tuple
        self.assertEqual(len(match), 2)
        self.assertEqual(match, (counter, time))
        self.assertRaises(IndexError, match.__getitem__, -3)
        self.assertEqual(match[0], counter)
        self.assertEqual(match[1], time)
        self.assertRaises(IndexError, match.__getitem__, 2)

        # test bool
        self.assertTrue(match)

    def test_totp_match_w_valid_token(self):
        """match() -- valid TotpMatch object"""
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda: time + 24 * 3600)(KEY3)
        result = otp.match(token, time)
        self.assertTotpMatch(result, time=time, skipped=0)

    def test_totp_match_w_older_token(self):
        """match() -- valid TotpMatch object with future token"""
        from passlib.totp import TotpMatch

        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda: time + 24 * 3600)(KEY3)
        result = otp.match(token, time - 30)
        self.assertTotpMatch(result, time=time - 30, skipped=1)

    def test_totp_match_w_new_token(self):
        """match() -- valid TotpMatch object with past token"""
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda: time + 24 * 3600)(KEY3)
        result = otp.match(token, time + 30)
        self.assertTotpMatch(result, time=time + 30, skipped=-1)

    def test_totp_match_w_invalid_token(self):
        """match() -- invalid TotpMatch object"""
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda: time + 24 * 3600)(KEY3)
        self.assertRaises(exc.InvalidTokenError, otp.match, token, time + 60)

    #=============================================================================
    # match() tests
    #=============================================================================

    def assertVerifyMatches(self, expect_skipped, token, time,  # *
                            otp, gen_time=None, **kwds):
        """helper to test otp.match() output is correct"""
        # NOTE: TotpMatch return type tested more throughly above ^^^
        msg = "key=%r alg=%r period=%r token=%r gen_time=%r time=%r:" % \
              (otp.base32_key, otp.alg, otp.period, token, gen_time, time)
        result = otp.match(token, time, **kwds)
        self.assertTotpMatch(result,
                             time=otp.normalize_time(time),
                             period=otp.period,
                             window=kwds.get("window", 30),
                             skipped=expect_skipped,
                             msg=msg)

    def assertVerifyRaises(self, exc_class, token, time,  # *
                          otp, gen_time=None,
                          **kwds):
        """helper to test otp.match() throws correct error"""
        # NOTE: TotpMatch return type tested more throughly above ^^^
        msg = "key=%r alg=%r period=%r token=%r gen_time=%r time=%r:" % \
              (otp.base32_key, otp.alg, otp.period, token, gen_time, time)
        return self.assertRaises(exc_class, otp.match, token, time,
                                 __msg__=msg, **kwds)

    def test_match_w_window(self):
        """match() -- 'time' and 'window' parameters"""

        # init generator & helper
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        token = otp.generate(time).token
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)

        #-------------------------------
        # basic validation, and 'window' parameter
        #-------------------------------

        # validate against previous counter (passes if window >= period)
        assertRaises(exc.InvalidTokenError, token, time - period, window=0)
        assertMatches(+1, token, time - period, window=period)
        assertMatches(+1, token, time - period, window=2 * period)

        # validate against current counter
        assertMatches(0, token, time, window=0)

        # validate against next counter (passes if window >= period)
        assertRaises(exc.InvalidTokenError, token, time + period, window=0)
        assertMatches(-1, token, time + period, window=period)
        assertMatches(-1, token, time + period, window=2 * period)

        # validate against two time steps later (should never pass)
        assertRaises(exc.InvalidTokenError, token, time + 2 * period, window=0)
        assertRaises(exc.InvalidTokenError, token, time + 2 * period, window=period)
        assertMatches(-2, token, time + 2 * period, window=2 * period)

        # TODO: test window values that aren't multiples of period
        #       (esp ensure counter rounding works correctly)

        #-------------------------------
        # time normalization
        #-------------------------------

        # handle datetimes
        dt = datetime.datetime.utcfromtimestamp(time)
        assertMatches(0, token, dt, window=0)

        # reject invalid time
        assertRaises(ValueError, token, -1)

    def test_match_w_skew(self):
        """match() -- 'skew' parameters"""
        # init generator & helper
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)

        # assume client is running far behind server / has excessive transmission delay
        skew = 3 * period
        behind_token = otp.generate(time - skew).token
        assertRaises(exc.InvalidTokenError, behind_token, time, window=0)
        assertMatches(-3, behind_token, time, window=0, skew=-skew)

        # assume client is running far ahead of server
        ahead_token = otp.generate(time + skew).token
        assertRaises(exc.InvalidTokenError, ahead_token, time, window=0)
        assertMatches(+3, ahead_token, time, window=0, skew=skew)

        # TODO: test skew + larger window

    def test_match_w_reuse(self):
        """match() -- 'reuse' and 'last_counter' parameters"""

        # init generator & helper
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        tdata = otp.generate(time)
        token = tdata.token
        counter = tdata.counter
        expire_time = tdata.expire_time
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)

        # last counter unset --
        # previous period's token should count as valid
        assertMatches(-1, token, time + period, window=period)

        # last counter set 2 periods ago --
        # previous period's token should count as valid
        assertMatches(-1, token, time + period, last_counter=counter-1,
                      window=period)

        # last counter set 2 periods ago --
        # 2 periods ago's token should NOT count as valid
        assertRaises(exc.InvalidTokenError, token, time + 2 * period,
                     last_counter=counter, window=period)

        # last counter set 1 period ago --
        # previous period's token should now be rejected as 'used'
        err = assertRaises(exc.UsedTokenError, token, time + period,
                           last_counter=counter, window=period)
        self.assertEqual(err.expire_time, expire_time)

        # last counter set to current period --
        # current period's token should be rejected
        err = assertRaises(exc.UsedTokenError, token, time,
                           last_counter=counter, window=0)
        self.assertEqual(err.expire_time, expire_time)

    def test_match_w_token_normalization(self):
        """match() -- token normalization"""
        # setup test helper
        otp = TOTP('otxl2f5cctbprpzx')
        match = otp.match
        time = 1412889861

        # separators / spaces should be stripped (orig token '332136')
        self.assertTrue(match('    3 32-136  ', time))

        # ascii bytes
        self.assertTrue(match(b'332136', time))

        # too few digits
        self.assertRaises(exc.MalformedTokenError, match, '12345', time)

        # invalid char
        self.assertRaises(exc.MalformedTokenError, match, '12345X', time)

        # leading zeros count towards size
        self.assertRaises(exc.MalformedTokenError, match, '0123456', time)

    def test_match_w_reference_vectors(self):
        """match() -- reference vectors"""
        for otp, time, token, expires, msg in self.iter_test_vectors():
            # create wrapper
            match = otp.match

            # token should match against time
            result = match(token, time)
            self.assertTrue(result)
            self.assertEqual(result.counter, time // otp.period, msg=msg)

            # should NOT match against another time
            self.assertRaises(exc.InvalidTokenError, match, token, time + 100, window=0)

    #=============================================================================
    # verify() tests
    #=============================================================================
    def test_verify(self):
        """verify()"""
        # NOTE: since this is thin wrapper around .from_source() and .match(),
        #       just testing basic behavior here.

        from passlib.totp import TOTP

        time = 1412889861
        TotpFactory = TOTP.using(now=lambda: time)

        # successful match
        source1 = dict(v=1, type="totp", key='otxl2f5cctbprpzx')
        match = TotpFactory.verify('332136', source1)
        self.assertTotpMatch(match, time=time)

        # failed match
        source1 = dict(v=1, type="totp", key='otxl2f5cctbprpzx')
        self.assertRaises(exc.InvalidTokenError, TotpFactory.verify, '332155', source1)

        # bad source
        source1 = dict(v=1, type="totp")
        self.assertRaises(ValueError, TotpFactory.verify, '332155', source1)

        # successful match -- json source
        source1json = '{"v": 1, "type": "totp", "key": "otxl2f5cctbprpzx"}'
        match = TotpFactory.verify('332136', source1json)
        self.assertTotpMatch(match, time=time)

        # successful match -- URI
        source1uri = 'otpauth://totp/Label?secret=otxl2f5cctbprpzx'
        match = TotpFactory.verify('332136', source1uri)
        self.assertTotpMatch(match, time=time)

    #=============================================================================
    # serialization frontend tests
    #=============================================================================
    def test_from_source(self):
        """from_source()"""
        from passlib.totp import TOTP
        from_source = TOTP.from_source

        # uri (unicode)
        otp = from_source(u("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                            "issuer=Example"))
        self.assertEqual(otp.key, KEY4_RAW)

        # uri (bytes)
        otp = from_source(b"otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                          b"issuer=Example")
        self.assertEqual(otp.key, KEY4_RAW)

        # dict
        otp = from_source(dict(v=1, type="totp", key=KEY4))
        self.assertEqual(otp.key, KEY4_RAW)

        # json (unicode)
        otp = from_source(u('{"v": 1, "type": "totp", "key": "JBSWY3DPEHPK3PXP"}'))
        self.assertEqual(otp.key, KEY4_RAW)

        # json (bytes)
        otp = from_source(b'{"v": 1, "type": "totp", "key": "JBSWY3DPEHPK3PXP"}')
        self.assertEqual(otp.key, KEY4_RAW)

        # TOTP object -- return unchanged
        self.assertIs(from_source(otp), otp)

        # TOTP object w/ different wallet -- return new one.
        wallet1 = AppWallet()
        otp1 = TOTP.using(wallet=wallet1).from_source(otp)
        self.assertIsNot(otp1, otp)
        self.assertEqual(otp1.to_dict(), otp.to_dict())

        # TOTP object w/ same wallet -- return original
        otp2 = TOTP.using(wallet=wallet1).from_source(otp1)
        self.assertIs(otp2, otp1)

        # random string
        self.assertRaises(ValueError, from_source, u("foo"))
        self.assertRaises(ValueError, from_source, b"foo")

    #=============================================================================
    # uri serialization tests
    #=============================================================================
    def test_from_uri(self):
        """from_uri()"""
        from passlib.totp import TOTP
        from_uri = TOTP.from_uri

        # URIs from https://code.google.com/p/google-authenticator/wiki/KeyUriFormat

        #--------------------------------------------------------------------------------
        # canonical uri
        #--------------------------------------------------------------------------------
        otp = from_uri("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                       "issuer=Example")
        self.assertIsInstance(otp, TOTP)
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertEqual(otp.label, "alice@google.com")
        self.assertEqual(otp.issuer, "Example")
        self.assertEqual(otp.alg, "sha1") # default
        self.assertEqual(otp.period, 30) # default
        self.assertEqual(otp.digits, 6) # default

        #--------------------------------------------------------------------------------
        # secret param
        #--------------------------------------------------------------------------------

        # secret case insensitive
        otp = from_uri("otpauth://totp/Example:alice@google.com?secret=jbswy3dpehpk3pxp&"
                       "issuer=Example")
        self.assertEqual(otp.key, KEY4_RAW)

        # missing secret
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?digits=6")

        # undecodable secret
        self.assertRaises(Base32DecodeError, from_uri, "otpauth://totp/Example:alice@google.com?"
                                                       "secret=JBSWY3DPEHP@3PXP")

        #--------------------------------------------------------------------------------
        # label param
        #--------------------------------------------------------------------------------

        # w/ encoded space
        otp = from_uri("otpauth://totp/Provider1:Alice%20Smith?secret=JBSWY3DPEHPK3PXP&"
                       "issuer=Provider1")
        self.assertEqual(otp.label, "Alice Smith")
        self.assertEqual(otp.issuer, "Provider1")

        # w/ encoded space and colon
        # (note url has leading space before 'alice') -- taken from KeyURI spec
        otp = from_uri("otpauth://totp/Big%20Corporation%3A%20alice@bigco.com?"
                       "secret=JBSWY3DPEHPK3PXP")
        self.assertEqual(otp.label, "alice@bigco.com")
        self.assertEqual(otp.issuer, "Big Corporation")

        #--------------------------------------------------------------------------------
        # issuer param / prefix
        #--------------------------------------------------------------------------------

        # 'new style' issuer only
        otp = from_uri("otpauth://totp/alice@bigco.com?secret=JBSWY3DPEHPK3PXP&issuer=Big%20Corporation")
        self.assertEqual(otp.label, "alice@bigco.com")
        self.assertEqual(otp.issuer, "Big Corporation")

        # new-vs-old issuer mismatch
        self.assertRaises(ValueError, TOTP.from_uri,
                          "otpauth://totp/Provider1:alice?secret=JBSWY3DPEHPK3PXP&issuer=Provider2")

        #--------------------------------------------------------------------------------
        # algorithm param
        #--------------------------------------------------------------------------------

        # custom alg
        otp = from_uri("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&algorithm=SHA256")
        self.assertEqual(otp.alg, "sha256")

        # unknown alg
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?"
                                                "secret=JBSWY3DPEHPK3PXP&algorithm=SHA333")

        #--------------------------------------------------------------------------------
        # digit param
        #--------------------------------------------------------------------------------

        # custom digits
        otp = from_uri("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=8")
        self.assertEqual(otp.digits, 8)

        # digits out of range / invalid
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=A")
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=%20")
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=15")

        #--------------------------------------------------------------------------------
        # period param
        #--------------------------------------------------------------------------------

        # custom period
        otp = from_uri("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&period=63")
        self.assertEqual(otp.period, 63)

        # reject period < 1
        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?"
                                                "secret=JBSWY3DPEHPK3PXP&period=0")

        self.assertRaises(ValueError, from_uri, "otpauth://totp/Example:alice@google.com?"
                                                "secret=JBSWY3DPEHPK3PXP&period=-1")

        #--------------------------------------------------------------------------------
        # unrecognized param
        #--------------------------------------------------------------------------------

        # should issue warning, but otherwise ignore extra param
        with self.assertWarningList([
            dict(category=exc.PasslibRuntimeWarning, message_re="unexpected parameters encountered")
        ]):
            otp = from_uri("otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                           "foo=bar&period=63")
        self.assertEqual(otp.base32_key, KEY4)
        self.assertEqual(otp.period, 63)

    def test_to_uri(self):
        """to_uri()"""

        #-------------------------------------------------------------------------
        # label & issuer parameters
        #-------------------------------------------------------------------------

        # with label & issuer
        otp = TOTP(KEY4, alg="sha1", digits=6, period=30)
        self.assertEqual(otp.to_uri("alice@google.com", "Example Org"),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                         "issuer=Example%20Org")

        # label is required
        self.assertRaises(ValueError, otp.to_uri, None, "Example Org")

        # with label only
        self.assertEqual(otp.to_uri("alice@google.com"),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP")

        # with default label from constructor
        otp.label = "alice@google.com"
        self.assertEqual(otp.to_uri(),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP")

        # with default label & default issuer from constructor
        otp.issuer = "Example Org"
        self.assertEqual(otp.to_uri(),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP"
                         "&issuer=Example%20Org")

        # reject invalid label
        self.assertRaises(ValueError, otp.to_uri, "label:with:semicolons")

        # reject invalid issue
        self.assertRaises(ValueError, otp.to_uri, "alice@google.com", "issuer:with:semicolons")

        #-------------------------------------------------------------------------
        # algorithm parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, alg="sha256").to_uri("alice@google.com"),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                         "algorithm=SHA256")

        #-------------------------------------------------------------------------
        # digits parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, digits=8).to_uri("alice@google.com"),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                         "digits=8")

        #-------------------------------------------------------------------------
        # period parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, period=63).to_uri("alice@google.com"),
                         "otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&"
                         "period=63")

    #=============================================================================
    # dict serialization tests
    #=============================================================================
    def test_from_dict(self):
        """from_dict()"""
        from passlib.totp import TOTP
        from_dict = TOTP.from_dict

        #--------------------------------------------------------------------------------
        # canonical simple example
        #--------------------------------------------------------------------------------
        otp = from_dict(dict(v=1, type="totp", key=KEY4, label="alice@google.com", issuer="Example"))
        self.assertIsInstance(otp, TOTP)
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertEqual(otp.label, "alice@google.com")
        self.assertEqual(otp.issuer, "Example")
        self.assertEqual(otp.alg, "sha1")  # default
        self.assertEqual(otp.period, 30)  # default
        self.assertEqual(otp.digits, 6)  # default

        #--------------------------------------------------------------------------------
        # metadata
        #--------------------------------------------------------------------------------

        # missing version
        self.assertRaises(ValueError, from_dict, dict(type="totp", key=KEY4))

        # invalid version
        self.assertRaises(ValueError, from_dict, dict(v=0, type="totp", key=KEY4))
        self.assertRaises(ValueError, from_dict, dict(v=999, type="totp", key=KEY4))

        # missing type
        self.assertRaises(ValueError, from_dict, dict(v=1, key=KEY4))

        #--------------------------------------------------------------------------------
        # secret param
        #--------------------------------------------------------------------------------

        # secret case insensitive
        otp = from_dict(dict(v=1, type="totp", key=KEY4.lower(), label="alice@google.com", issuer="Example"))
        self.assertEqual(otp.key, KEY4_RAW)

        # missing secret
        self.assertRaises(ValueError, from_dict, dict(v=1, type="totp"))

        # undecodable secret
        self.assertRaises(Base32DecodeError, from_dict,
                          dict(v=1, type="totp", key="JBSWY3DPEHP@3PXP"))

        #--------------------------------------------------------------------------------
        # label & issuer params
        #--------------------------------------------------------------------------------

        otp = from_dict(dict(v=1, type="totp", key=KEY4, label="Alice Smith", issuer="Provider1"))
        self.assertEqual(otp.label, "Alice Smith")
        self.assertEqual(otp.issuer, "Provider1")

        #--------------------------------------------------------------------------------
        # algorithm param
        #--------------------------------------------------------------------------------

        # custom alg
        otp = from_dict(dict(v=1, type="totp", key=KEY4, alg="sha256"))
        self.assertEqual(otp.alg, "sha256")

        # unknown alg
        self.assertRaises(ValueError, from_dict, dict(v=1, type="totp", key=KEY4, alg="sha333"))

        #--------------------------------------------------------------------------------
        # digit param
        #--------------------------------------------------------------------------------

        # custom digits
        otp = from_dict(dict(v=1, type="totp", key=KEY4, digits=8))
        self.assertEqual(otp.digits, 8)

        # digits out of range / invalid
        self.assertRaises(TypeError, from_dict, dict(v=1, type="totp", key=KEY4, digits="A"))
        self.assertRaises(ValueError, from_dict, dict(v=1, type="totp", key=KEY4, digits=15))

        #--------------------------------------------------------------------------------
        # period param
        #--------------------------------------------------------------------------------

        # custom period
        otp = from_dict(dict(v=1, type="totp", key=KEY4, period=63))
        self.assertEqual(otp.period, 63)

        # reject period < 1
        self.assertRaises(ValueError, from_dict, dict(v=1, type="totp", key=KEY4, period=0))
        self.assertRaises(ValueError, from_dict, dict(v=1, type="totp", key=KEY4, period=-1))

        #--------------------------------------------------------------------------------
        # unrecognized param
        #--------------------------------------------------------------------------------
        self.assertRaises(TypeError, from_dict, dict(v=1, type="totp", key=KEY4, INVALID=123))

    def test_to_dict(self):
        """to_dict()"""

        #-------------------------------------------------------------------------
        # label & issuer parameters
        #-------------------------------------------------------------------------

        # without label or issuer
        otp = TOTP(KEY4, alg="sha1", digits=6, period=30)
        self.assertEqual(otp.to_dict(), dict(v=1, type="totp", key=KEY4))

        # with label & issuer from constructor
        otp = TOTP(KEY4, alg="sha1", digits=6, period=30,
                   label="alice@google.com", issuer="Example Org")
        self.assertEqual(otp.to_dict(),
                         dict(v=1, type="totp", key=KEY4,
                              label="alice@google.com", issuer="Example Org"))

        # with label only
        otp = TOTP(KEY4, alg="sha1", digits=6, period=30,
                   label="alice@google.com")
        self.assertEqual(otp.to_dict(),
                         dict(v=1, type="totp", key=KEY4,
                              label="alice@google.com"))

        # with issuer only
        otp = TOTP(KEY4, alg="sha1", digits=6, period=30,
                   issuer="Example Org")
        self.assertEqual(otp.to_dict(),
                         dict(v=1, type="totp", key=KEY4,
                              issuer="Example Org"))

        # don't serialize default issuer
        TotpFactory = TOTP.using(issuer="Example Org")
        otp = TotpFactory(KEY4)
        self.assertEqual(otp.to_dict(), dict(v=1, type="totp", key=KEY4))

        # don't serialize default issuer *even if explicitly set*
        otp = TotpFactory(KEY4, issuer="Example Org")
        self.assertEqual(otp.to_dict(),  dict(v=1, type="totp", key=KEY4))

        #-------------------------------------------------------------------------
        # algorithm parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, alg="sha256").to_dict(),
                         dict(v=1, type="totp", key=KEY4, alg="sha256"))

        #-------------------------------------------------------------------------
        # digits parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, digits=8).to_dict(),
                         dict(v=1, type="totp", key=KEY4, digits=8))

        #-------------------------------------------------------------------------
        # period parameter
        #-------------------------------------------------------------------------
        self.assertEqual(TOTP(KEY4, period=63).to_dict(),
                         dict(v=1, type="totp", key=KEY4, period=63))

    # TODO: to_dict()
    #           with encrypt=False
    #           with encrypt="auto" + wallet + secrets
    #           with encrypt="auto" + wallet + no secrets
    #           with encrypt="auto" + no wallet
    #           with encrypt=True + wallet + secrets
    #           with encrypt=True + wallet + no secrets
    #           with encrypt=True + no wallet
    #           that 'changed' is set for old versions, and old encryption tags.

    #=============================================================================
    # json serialization tests
    #=============================================================================

    # TODO: from_json() / to_json().
    #       (skipped for right now cause just wrapper for from_dict/to_dict)

    #=============================================================================
    # eoc
    #=============================================================================

#=============================================================================
# eof
#=============================================================================
