# txc.py  (c)2020  Henrique Moreira (part of 'waxpage')

"""
TXC - TeXt with Context

Compatibility: python 3.
"""

# pylint: disable=unused-argument


import sys
import os
from waxpage.redit import char_map, LATIN1_TEXT

VALID_CODE_NAMES = (
    "ISO-8859-1",
    "UTF-8",
    )

SPECIAL_TXC = (
    ".txc",
    )

DEF_DUMP_OPTS = {
    "verbose": 0,
    "simplify": True,
    "encode-out": "",
    }

DEF_TXC_TOLERATIONS = {
    "header-mismatch-basename": False,
    "last-line-empty": True,
    "first-line-empty": False,
    }


def main():
    """ Main test script! """
    prog = __file__
    char_map.allow_symbols()
    code = dump(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} [options] filename [filename ...]

Options are:
   -v          Verbose mode (shows Latin-1 accents, etc.)
   -n          No Latin-1 simplification
   -e X Y      Encode as X to output file Y (e.g. X='latin-1')
""")
    # Example:
    #	python txc -v -e latin-1 /tmp/out.txt a.txc
    sys.exit(code if code else 0)


def dump(out, err, args) -> int:
    """ Dump file(s) """
    # Header example:	#-*- coding: ISO-8859-1 -*-
    verbose = 0
    simplify = DEF_DUMP_OPTS["simplify"]
    out_encode = DEF_DUMP_OPTS["encode-out"]
    param = args
    while param and param[0].startswith("-"):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            verbose += 1
            continue
        if param[0] in ("-n", "--no"):
            del param[0]
            simplify = False
            continue
        if param[0] in ("-e", "--encode-out"):
            out_encode = param[1]
            out = open(param[2], "wb")
            del param[:3]
            continue
        return None
    opts = {"verbose": verbose,
            "simplify": simplify,
            "encode-out": out_encode,
            }
    if not param:
        return None
    code = dump_texts(out, param, opts)
    return code


def dump_texts(out, param, opts, debug=0) -> int:
    """ Dump text files """
    for name in param:
        code = dump_file(out, name, name.endswith(SPECIAL_TXC), opts)
        if code != 0:
            return code
    return 0


def dump_file(out, name, do_txc, opts=None) -> int:
    """ Dump (text-like) file """
    if opts is None:
        opts = DEF_DUMP_OPTS
    verbose = opts["verbose"]
    kind = 1 if (do_txc or verbose > 0) else 0
    _, data, codex = read_txc(name, do_txc)
    if do_txc:
        shown = data.strip() + "\n"
    else:
        shown = data
    if not out:
        return 0
    streamed = out != sys.stdout
    if opts["encode-out"]:
        out_encode = opts["encode-out"]
        streamed = True
    else:
        out_encode = codex
    if opts["simplify"]:
        if streamed:
            out.write(char_map.simpler_ascii(shown, kind).encode("ascii"))
        else:
            out.write(char_map.simpler_ascii(shown, kind))
    else:
        if streamed:
            out.write(shown.encode(out_encode))
        else:
            out.write(shown)
    return 0


def read_txc(name, do_txc):
    """ Reads TXC (or plain-text) file """
    codex, offset = "", 0
    with open(name, "rb") as fbin:
        head = fbin.read(32)
    try:
        com = head.decode("ascii").splitlines()[0]
    except UnicodeDecodeError:
        com = ""
    if com.startswith("#-*-"):
        codex, _ = what_code(com[len("#-*-"):].split("-*-")[0])
        offset = len(com) + 1
    if not codex:
        codex = LATIN1_TEXT
    with open(name, "r", encoding=codex) as file:
        data = file.read()[offset:]
    return offset, data, codex


def what_code(coding) -> tuple:
    """ Returns the code name and kind of 'coding' from string """
    assert isinstance(coding, str)
    astr = coding.strip().split(":", maxsplit=1)
    s_coding = astr[0]
    code_name = astr[1].strip()
    if "-" in code_name:
        assert code_name in valid_code_names()
    else:
        code_name = "ascii"
    return code_name, s_coding


def valid_code_names():
    """ Returns a list/ tuple with valid code name(s) string(s) """
    return VALID_CODE_NAMES



class FileText():
    """ Basic class with utilities, for text files. """
    # pylint: disable=no-self-use, too-few-public-methods

    _payload_start = 0	# line where payload starts
    _separation = 0

    def _from_fname(self, astr):
        """ Returns the applicable header string from filename """
        res = char_map.simpler_ascii(astr)
        return res


class FileTXC(FileText):
    """ File of type: TeXt with Context """

    # pylint: disable=too-many-instance-attributes

    name, _extension = "", ""
    msg = (0, "")
    tolerate = DEF_TXC_TOLERATIONS

    def __init__(self, name=None):
        _valid_exts = (".txc", ".txt")
        self._separation = 1
        self.error, self.data, self.codex = 0, "", ""
        self._payload_start = 0
        self.lines, self.nodes = list(), list()
        self._init_txc(name, _valid_exts)

    def _init_txc(self, name, valid_exts):
        aname = name
        if name:
            self._read_text(name)
        else:
            aname = ""
        if aname:
            aname = os.path.basename(aname)
        ext = ("."+aname.split(".")[-1]) if "." in aname else ""
        self.name = aname[:-len(ext)] if ext in valid_exts else aname
        self._extension = ext

    def set_style(self, style=""):
        """ Sets toleration according 'style' entered.
            Styles are as follow:
		- 'text' - text-alike list
        """
        assert isinstance(style, str)
        dct = DEF_TXC_TOLERATIONS
        if style == "":
            pass
        elif style == "text":
            dct["header-mismatch-basename"] = False
            dct["first-line-empty"] = True
        else:
            dct = None
        assert dct
        self.tolerate = dct

    def _read_text(self, name) -> bool:
        """ Reads TXC content """
        error = 0
        tup = (0, "", "ascii")
        try:
            tup = read_txc(name, True)
        except FileNotFoundError:
            error = 2
        offset, text, self.codex = tup
        if offset:
            self._payload_start = 1
            if text.startswith('\n'):
                self._payload_start += 1
        # Ignore first newline if file started with e.g. #-*- ISO-8859-1 -*-
        payload = text[int(self._payload_start > 1):]
        self.data = payload
        self.error = error
        if "\n\n\n" in payload:
            self._separation = 2
        return error == 0

    def all_ok(self) -> bool:
        """ Returns True if there are no bogus """
        return self.error == 0

    def parse(self) -> bool:
        """ Returns True if file was successfully parsed.
        """
        lines = self.data.splitlines()
        nodes = list()
        is_ok, last_msg = self._parse_txc(lines, nodes)
        self.msg = last_msg
        if is_ok:
            self.nodes = nodes
            self.lines = lines
        return is_ok

    def _parse_txc(self, lines, nodes) -> tuple:
        # pylint: disable=too-many-branches
        if not lines:
            return True
        has_head = lines[0].startswith("# ")
        hdr = Node("header", (lines[0][2:],) if has_head else None)
        nodes.append(hdr)
        is_ok = hdr.linestr() == hdr.linestr().strip()
        if not is_ok:
            return False, (1, "Header is not trimmed")
        if has_head:
            is_ok = self._from_fname(self.name) == hdr.linestr()
            if not is_ok:
                is_ok = self._from_fname(self.name) + self._extension == hdr.linestr()
            idx = 1
            there = lines[idx]
            if there:
                return False, (2, "Expected blank after header")
            idx += 1
        else:
            idx = 0
        if not is_ok:
            if not self.tolerate["header-mismatch-basename"]:
                return False, (1, "Header mismatches file basename")
        payload = lines[idx:]
        line_nr, pline = idx + self._payload_start, 0
        empties = 0
        series = list()
        for line in payload:
            pline += 1
            line_nr += 1
            if line == "":
                empties += 1
                if series:
                    node = Node("item", series)
                    nodes.append(node)
                else:
                    if pline <= 1 and self.tolerate["first-line-empty"]:
                        pass
                    else:
                        if empties != self._separation:
                            amsg = f"Unexpected empty line (separation={self._separation})"
                            if self._separation > 1:
                                return False, (line_nr, amsg)
                            return False, (line_nr, "Unexpected empty line")
                    nodes.append(Node("blank"))
                series = list()
            else:
                if len(nodes) > 1 and not series:
                    amsg = f"Two few empty lines ({empties}, expected {self._separation})"
                    # Check if preceeding lines are ok
                    if empties < self._separation:
                        return False, (line_nr, amsg)
                series.append(line)
                empties = 0
            idx += 1
        if series:
            if not self.tolerate["last-line-empty"]:
                return False, (line_nr, "Last line should be empty")
            node = Node("item", series)
            nodes.append(node)
        return True, (0, "")


class Node():
    """ Text node (TXC) """
    _VALID_NODES = (
        "header",
        "mark",
        "item",
        "blank",
        )

    def __init__(self, kind, lines=None):
        what = lines if lines else list()
        assert isinstance(what, (list, tuple))
        self.kind = kind
        self.lines = what
        assert kind in Node._VALID_NODES

    def node_kind(self) -> str:
        """ Returns the node kind! """
        return self.kind

    def linestr(self) -> str:
        """ Returns the lines list as a single string """
        if not self.lines:
            return ""
        assert len(self.lines) == 1
        return self.lines[0]

    def as_string(self) -> str:
        """ Return node as string """
        res = f"'{self.kind}'={self.lines}"
        return res


#
# Test suite
#
if __name__ == "__main__":
    main()
