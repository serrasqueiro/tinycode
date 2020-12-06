# dumper.py  (c)2020  Henrique Moreira (part of 'waxpage')

"""
Dumps files as text pages, best-effort.

Default output encoding is LATIN-1 (aka ISO-8859-1)
"""

# pylint: disable=unused-argument


import sys
import waxpage.redit as redit


### Constants ###

_VERBOSE = False
# https://tools.ietf.org/html/rfc3629#section-3
_TRY_READ_AS_UTF8 = True
#_TRY_READ_AS_UTF8 = False	# uncomment if you prefer this default

UTF8_EXCLUDE = (".txu",		# Extensions to exclude from reading UTF-8
               )

DEF_ENCODE_OUT = redit.LATIN1_TEXT	# "ISO-8859-1"

### The script ... ###

def main():
    """ Main test script! """
    prog = __file__
    msg = f"""Usage:

{prog} [filename]

Options:
   -v              Verbose mode
   -s              Simple ASCII output (or --simple)
   --try-latin-1   Try reading Latin-1 (or --try-ISO-8859-1)
"""
    if not _TRY_READ_AS_UTF8:
        msg += """   --try           Try using UTF-8 as input
"""
    msg += f"\nUse\n   {prog} -h (or --help)\nto show this help."
    code = dumper(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(msg)
    sys.exit(code if code else 0)


def dumper(out, err, args):
    """ Main module test! """
    opts = {"verbose": 0,
            "simple": False,
            "try-input": "",
            "try-utf8": _TRY_READ_AS_UTF8,
            "enc-out": DEF_ENCODE_OUT,
            "out": None,
            }
    param = args
    while param and param[0].startswith("-"):
        if param[0] == '-v':
            del param[0]
            opts["verbose"] += 1
            continue
        if param[0] in ('--simple', '-s'):
            del param[0]
            opts["simple"] = True
            continue
        if param[0] == '--try':
            del param[0]
            opts["try-utf8"] = True
            continue
        if param[0] in ('--try-latin-1',
                        '--try-ISO-8859-1',
                        ):
            opts["try-utf8"] = False
            opts["try-input"] = param[0][len("--try-"):]
            del param[0]
            continue
        if param[0] in ('--out', '-o'):
            assert not opts["out"]
            opts["out"] = param[1]
            del param[:2]
            continue
        return None
    if param:
        files = param
        for name in files:
            assert not name.startswith("-")
    else:
        files = [None]
    if opts["out"]:
        out_file = open(opts["out"], "wb")
    else:
        out_file = out
    errs = dump(out_file, redit.char_map, files, opts)
    code = 0 if not errs else 1
    if errs:
        idx = 0
        for line, _, simple in errs:
            idx += 1
            err.write(f"Error {idx} of {len(errs)}: line {line}, error writing: {simple}\n")
    return code


def dump(out, charmap, param, opts, debug=0) -> list:
    """ Dump files """
    errs = []
    try_input = opts["try-input"]
    enc_in = "UTF-8" if opts["try-utf8"] else None
    if try_input:
        enc_in = try_input
    enc_out = opts["enc-out"]
    idx, verbose = 0, opts["verbose"]
    for name in param:
        is_stdin = name is None
        if is_stdin:
            file = sys.stdin
        else:
            assert name
            if verbose > 0:
                print(f"Reading {name} as: {enc_in}")
            file = open(name, "r", encoding=enc_in)
        data = file.read()
        lines = data.splitlines()
        for line in lines:
            idx += 1
            astr = line
            astr = string_safe(astr)
            simple = charmap.simpler_ascii(astr)
            if opts["simple"]:
                astr = simple
            if verbose > 0:
                if len(astr) > 78 or not astr.strip():
                    shown = ""
                else:
                    shown = f": {simple}"
                print(f"Line {idx}, write {len(astr)} byte(s){shown}")
            if opts["out"]:
                try:
                    out.write(bytes(astr, enc_out))
                except UnicodeEncodeError:
                    errs.append((idx, astr, simple))
                out.write(bytes("\n", "ascii"))
            else:
                out.write(astr)
                out.write("\n")
    return errs


def string_safe(astr) -> str:
    """ Returns a string that can be displayed """
    res = astr.replace('\u2022', '-o-')
    return res


# Main script
if __name__ == "__main__":
    main()
