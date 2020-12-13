# txc.py  (c)2018, 2020  Henrique Moreira (part of 'waxpage')

"""
TXC - TeXt with Context

Compatibility: python 3.
"""

# pylint: disable=unused-argument


import sys
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
    code, data, codex = read_txc(name, do_txc)
    if do_txc:
        shown = data.strip() + "\n"
    else:
        shown = data
    if not out:
        return code
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
    return code


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
    return 0, data, codex


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


#
# Test suite
#
if __name__ == "__main__":
    main()
