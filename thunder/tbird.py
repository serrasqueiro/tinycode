# tbird.py  (c)2021  Henrique Moreira (part of 'drotag')

"""
tbird -- parses Thunderbird prefs.js

Compatibility: python 3.
"""

# pylint: disable=missing-function-docstring

import sys
import re


BASIC_DICT = {
    "@mail.server": dict(),
    }

IGNORED_MAIL_ITEMS = (
    "serverIDResponse",
    )


def main():
    """ Main tests """
    code = basic_test(sys.argv[1:])
    sys.exit(int(code) if code else 0)


def basic_test(args) -> int:
    param = args
    for fname in param:
        print("Parsing prefs.js:", fname)
        prefs = Prefs(fname)
        is_ok = prefs.parse()
        assert is_ok
        for item in prefs.cont:
            print("ITEM:", item)
        print("--\n@mail.server:")
        keys = sorted_alpha(prefs.assign["@mail.server"].keys())
        for key in keys:
            print("mail.server", key, ":::")
            dct = prefs.assign["@mail.server"][key]
            assert isinstance(dct, dict)
            for prop in sorted_alpha(dct.keys()):
                if prop in IGNORED_MAIL_ITEMS:
                    continue
                left, right = prop, coarse_val(dct[prop])
                print(f"	{left} = {right}")
            print("")
    return 0


class Content():
    """ Abstract class to handle contents
    """
    err, _errors = sys.stderr, 0
    cont = list()

    def num_errors(self):
        return self._errors


class Prefs(Content):
    """ Thunderbird Preferences (prefs.js) parser
    """

    lines = list()
    assign = None

    def __init__(self, fname=""):
        self.lines = list()
        self._errors, self.cont = 0, list()
        self.assign = BASIC_DICT
        if fname:
            self._read_file(fname)
        rex = r'user_pref\("(?P<left>[^"]*)", (?P<right>.*)\);'
        self.decl_rex = re.compile(rex)

    def _read_file(self, fname):
        self.lines = open(fname, "r").readlines()

    def parse(self) -> bool:
        idx = 0
        for line in self.lines:
            is_ok = True
            idx += 1
            if not line.strip() or line.startswith("//"):
                continue
            assert line.strip() != line
            matches = self.decl_rex.match(line)
            if matches:
                is_ok = self._add(line, matches)
            else:
                if self.err:
                    self.err.write(f"Ignored line {idx}: {line}\n")
            if not is_ok:
                self._errors += 1
                if self.err:
                    self.err.write(f"Invalid line {idx}: {line}\n")
        return self._errors == 0

    def _add(self, line, matched) -> bool:
        specials = ("mail.server",
                    )
        assert line
        left = matched.group(1)
        right = matched.group(2)
        self.cont.append((left, right))
        assert left not in self.assign
        self.assign[left] = right
        for tag in specials:
            dct = self.assign["@mail.server"]
            if left.startswith(tag + "."):
                prop = left[len(tag) + 1:]
                # prop e.g.	'server5.directory'
                aname, rest = prop.split(".", maxsplit=1)
                if aname not in dct:
                    dct[aname] = {rest: right}
                else:
                    dct[aname][rest] = right
        return True


def sorted_alpha(alist) -> list:
    """ Sorts alphabetically, ignoring upper-/ lowercase. """
    return sorted(alist, key=str.casefold)


def coarse_val(val) -> str:
    """ Returns a more readable string """
    assert isinstance(val, str)
    astr = val.replace("\\\\", "/")
    if astr.startswith('"') and astr.endswith('"'):
        astr = astr[1:-1]
    return astr


#
# Test suite
#
if __name__ == "__main__":
    main()
