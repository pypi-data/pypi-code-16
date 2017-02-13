import re

_POWERS = {
	"": 0,
	"k": 1,
	"m": 2,
	"g": 3,
	"t": 4,
	"p": 5,
	"e": 6,
	"z": 7,
	"y": 8,
}
_FORMAT_PATTERN = re.compile("^(\\d+)\\s*([%s]i?|)b?$" % "".join(_POWERS.keys()), flags=re.IGNORECASE)

def _base(suffix):
	# type: (str) -> int
	return 1024 if len(suffix) >= 2 and suffix[1].lower() == "i" else 1000

def _power(suffix):
	# type: (str) -> int
	suffix = suffix[:1]
	return _POWERS[suffix]

class SizeParseError(ValueError):
	pass

def parse(value):
	# type: (str) -> int
	matcher = _FORMAT_PATTERN.match(value)
	if matcher == None:
		raise SizeParseError("Parsing \"%s\" as a byte quantity failed." % value)
	number = int(matcher.group(1))
	suffix = matcher.group(2).lower()
	base = _base(suffix)
	power = _power(suffix)
	return number * (base ** power)
