# txcompiler.py  (c)2021  Henrique Moreira
#
# Based on CVS picky_txc.py; now at tinycode/ at github

"""
Picky TXC (text-file) compiler.
"""

# pylint: disable=unused-argument


import sys
from waxpage.redit import char_map
from waxpage.txc import read_txc, FileTXC


def main():
    """ Main test script! """
    prog = __file__
    char_map.allow_symbols()
    code = runner(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} command [options] filename [filename ...]

Commands are:
   check       Checks and dumps basic TXC content

   test        Tests TXC content

Options are:
   -v          Verbose mode (shows Latin-1 accents, etc.)
""")
    # Example:
    #	python txcompiler.py -v -e latin-1 /tmp/out.txt a.txc
    sys.exit(code if code else 0)


def runner(out, err, args):
    """ Dump file(s) """
    verbose = 0
    if not args:
        return None
    cmd = args[0]
    param = args[1:]
    while param and param[0].startswith("-"):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            verbose += 1
            continue
        return None
    opts = {"verbose": verbose,
            }
    if not param:
        return None
    if cmd == "check":
        code = check(out, err, param, opts)
        return code
    if cmd == "test":
        code = check(None, err, param, opts)
        return code
    return None


def check(out, err, param, opts) -> int:
    """ Check TXC files """
    result = 0
    verbose = opts["verbose"]
    for name in param:
        code, msgs = check_file(out, name, opts)
        if code == 0:
            if verbose > 0 or out is None:
                print("Checked:", name)
        else:
            _, first = msgs[0]
            err.write(f"Failed {name}: error-code {code}: {first}\n")
            for line, msg in msgs:
                err.write(f"{name}:line {line}: {msg}\n")
            if result == 0:
                result = code
    return result


def check_file(out, name, opts):
    """ Check TXC file"""
    # pylint: disable=line-too-long
    assert name
    msgs = list()
    verbose = opts["verbose"]
    tfile = FileTXC(name)
    tfile.set_style("text")
    if tfile.error:
        return tfile.error, ["Invalid txc"]
    is_ok = tfile.parse()
    nlines = len(tfile.lines)
    if tfile.msg:
        msgs.append(tfile.msg)
    if verbose > 0:
        print(f"{tfile.name}, parse() OK? {is_ok}: error={tfile.error}, codex={tfile.codex}, size={len(tfile.data)}, nlines={nlines}")
    if not is_ok:
        return 1, msgs
    if verbose >= 2:
        dump_everything(out, name, tfile)
        return 0, msgs
    for node in tfile.nodes:
        msg = nodified(node)
        if out:
            out.write(f"{msg}\n")
    return 0, msgs


def dump_everything(out, path, tfile):
    """ Dump everything at path """
    for node in tfile.nodes:
        shown = nodified(node)
        out.write(f"{path}: {shown}\n")


def nodified(node) -> str:
    """ Returns a string-ified node. """
    shown = char_map.simpler_ascii(node.lines, 1)
    astr = f"{node.kind}={shown}"
    return astr


# Main script
if __name__ == "__main__":
    main()
