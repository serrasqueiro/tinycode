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


def main():
    """ Main test script! """
    prog = __file__
    code = dump(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} [filename]
""")
    sys.exit(code if code else 0)


def dump(out, err, args) -> int:
    """ Dump file(s) """
    # Header example:	#-*- coding: ISO-8859-1 -*-
    verbose = 0
    param = args
    while param and param[0].startswith("-"):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            verbose += 1
            continue
        return None
    opts = {"verbose": verbose,
            }
    code = dump_texts(out, param, opts)
    return code


def dump_texts(out, param, opts, debug=0) -> int:
    """ Dump text files """
    for name in param:
        code = dump_file(out, name, name.endswith(SPECIAL_TXC), opts)
        if code != 0:
            return code
    return 0


def dump_file(out, name, do_txc, opts):
    """ Dump (text-like) file """
    codex = ""
    verbose = opts["verbose"]
    kind = 1 if (do_txc or verbose > 0) else 0
    with open(name, "rb") as fbin:
        head = fbin.read(32)
    try:
        com = head.decode("ascii").splitlines()[0]
    except UnicodeDecodeError:
        com = ""
    if com.startswith("#-*-"):
        codex, _ = what_code(com[len("#-*-"):].split("-*-")[0])
    if not codex:
        codex = LATIN1_TEXT
    with open(name, "r", encoding=codex) as file:
        data = file.read()
        out.write(char_map.simpler_ascii(data, kind))
    return 0


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
