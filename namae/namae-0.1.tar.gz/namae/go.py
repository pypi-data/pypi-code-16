import re
from . import titleize


class NameFormatter:
    def format(self, s,
               num_rx=re.compile("\d{2,}"),
               exclude_rx=re.compile("[^a-z0-9]", re.IGNORECASE | re.MULTILINE)):
        if not s:
            return ""
        elif num_rx.match(s):
            return self.format("Num" + s)
        elif s[0] in self.NUMBERS:
            return self.format(self.NUMBERS[s[0]] + s[1:])
        else:
            return exclude_rx.sub("", self.proper_acronym(s))

    def proper_acronym(self, s,
                       rx=re.compile("(?P<sep>^|[^a-zA-Z])(?P<frag>[a-z]+)", re.M),
                       rx2=re.compile("(?P<sep>[A-Z])(?P<frag>[a-z]+)", re.M)):
        return rx2.sub(self._proper_repl2, rx.sub(self._proper_repl1, s))

    NUMBERS = {
        '0': "Zero_", '1': "One_", '2': "Two_", '3': "Three_",
        '4': "Four_", '5': "Five_", '6': "Six_", '7': "Seven_",
        '8': "Eight_", '9': "Nine_"
    }

    # https://github.com/golang/lint/blob/39d15d55e9777df34cdffde4f406ab27fd2e60c0/lint.go#L695-L731
    COMMON_INITIALISMS = [
        "API", "ASCII", "CPU", "CSS", "DNS", "EOF", "GUID", "HTML", "HTTP",
        "HTTPS", "ID", "IP", "JSON", "LHS", "QPS", "RAM", "RHS", "RPC", "SLA",
        "SMTP", "SSH", "TCP", "TLS", "TTL", "UDP", "UI", "UID", "UUID", "URI",
        "URL", "UTF8", "VM", "XML", "XSRF", "XSS"
    ]

    def _proper_repl1(self, m):
        d = m.groupdict()
        if d["frag"].upper() in self.COMMON_INITIALISMS:
            return d["sep"] + d["frag"].upper()
        else:
            return d["sep"] + titleize(d["frag"])

    def _proper_repl2(self, m):
        d = m.groupdict()
        merged = d["sep"] + d["frag"]
        if merged.upper() in self.COMMON_INITIALISMS:
            return merged.upper()
        else:
            return merged


def goname(s, formatter=NameFormatter()):
    return formatter.format(s)
