# redit.test.py  (c)2018, 2020  Henrique Moreira (part of 'waxpage')

"""
  Test 'redit' module

  Compatibility: python 3.
"""

# pylint: disable=invalid-name


import sys
from waxpage.redit import char_map, CharMap, BareText, \
     LATIN1_TEXT
from waxpage.txc import SPECIAL_TXC

_VERBOSE = False
_READ_AS_UTF = False


def main():
    """ Main test script! """
    prog = __file__
    code = test_redit_test(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} [filename]
""")
    sys.exit(code if code else 0)


def test_redit_test(out, err, args) -> int:
    """ Main module test! """
    def test_show(charmap) -> int:
        assert isinstance(charmap, CharMap)
        s = "T\xe1bua no ch\xe3o em (C\xd4TE) C\xf4te d'Ivoire"
        for kind in (0, 1):
            text = charmap.simpler_ascii(s, kind)
            print(text)
            is_ok = text in ("Tabua no chao em (COTE) Cote d'Ivoire",
                             "Ta'bua no cha~o em (CO^TE) Co^te d'Ivoire",
                             )
            assert is_ok
        return 0

    assert err
    debug = 0 if not _VERBOSE else 1
    opts = {"dosCR": "",
            }
    param = args
    while param and param[0].startswith("-"):
        if param[ 0 ]=='--dos':
            del param[ 0 ]
            opts["dosCR"] = "\r"
            continue
        return None
    if param:
        code = dump_texts(out, param, opts, debug)
    else:
        code = test_show(char_map)
        try_markdown("howto.md")
    return code


def dump_texts(out, param, opts, debug=0) -> int:
    """ Dump text files """
    for name in param:
        if len(param) > 1:
            print("# dump_text:", name)
        dump_text(out, name, opts, debug)
    return 0


def dump_text(out, name, opts, debug=0) -> int:
    """ Dump one text file """
    if name.endswith(SPECIAL_TXC):
        with open(name, "r", encoding=LATIN1_TEXT) as file:
            data = file.read()
            print(char_map.simpler_ascii(data))
        return 0

    tred = BareText(name)
    if _READ_AS_UTF:
        is_ok = tred.utf_file_reader()
    else:
        is_ok = tred.file_reader()
    print("tred, ok?{}: {}".format(is_ok, tred))
    if is_ok:
        for line in tred.lines:
            out.write(line + opts["dosCR"] + "\n")
    print("Debug:", name)
    if debug > 0:
        dump_bare(out, tred)
    return 0


def try_markdown(md_file) -> int:
    """ Try to check pangram at markdown! """
    pangram = ""
    tal = 0
    try:
        file = open(md_file, "r", encoding=LATIN1_TEXT)
    except FileNotFoundError:
        file = None
    if file is None:
        print("Skipped test (file not there):", md_file)
        return 2
    lines = file.read().splitlines()
    for line in lines:
        if line.startswith(">"):
            pangram = line[1:].strip()
            break
    tred = BareText(md_file)
    #tred.file_reader()
    tred.add_from_buffer(pangram)
    hist = tred.histogram
    shown = char_map.simpler_ascii(pangram)
    print(f"Pangram (len={len(pangram)}): '{shown}'")
    for letter in char_map.lowercase():
        outras = 0
        upper = letter.upper()
        count = hist.seen[ord(letter)]
        count += hist.seen[ord(upper)]
        for oth in range(128, 256):
            letra = char_map.simpler_ascii(chr(oth))
            if letra == letter:
                outras += hist.seen[oth]
        print("Letter {}: {} {}{}".
              format(upper, count, outras,
                     f" (sum: {count+outras})" \
                     if outras else ""),
              tal)
        tal += count + outras
    count, outras, unconv = 0, 0, []
    for letter in pangram:
        num = ord(letter)
        letra = char_map.simpler_ascii(letter)
        if letra.isalpha():
            count += 1
            outras += int(num >= 128)
        else:
            if num >= 128:
                note = f"symbol={num}d, hex=0x{num:02x}"
                unconv.append(note)
    nunc = len(unconv)
    is_ok = shown == get_pangram("pt")
    print(f"Letter (all): {tal}+{nunc}, {count+outras} ({count}+{outras})",
          f"ok? {is_ok}")
    print(f"""
Example:
	94 un-accented letters from pangram;
	1 unconverted (in this case {nunc})
	107 letters from pangram (including accented): ({count}+{outras})
""")
    if unconv:
        print("Unconverted follows:\n" + "\n".join(unconv))
    assert is_ok
    return 0


def get_pangram(country="pt") -> str:
    """ Returns a selected pangram depending on country. """
    expected = ""
    if country == "pt":
        expected = "A noite, vovo Kowalsky ve o ima cair " + \
                   "no pe do ping.im queixoso e vovo poe acucar " + \
                   "no cha de tamaras do jabuti feliz (no pais)."
    assert expected
    return expected


def dump_bare(out, tred, exclude=None, debug=0):
    """ Dump nearly all BareText() variables. """
    assert isinstance(debug, int)
    if exclude is None:
        exc = ("buf", "lines",)	# do not show complete text...
    else:
        exc = exclude
    info = dir(tred)
    if out is not None:
        for mark in info:
            if mark[0] == "_" or mark in exc:
                continue
            val = vars(tred).get(mark)
            if val is None:
                out.write("non-var: {}()\n".format(mark))
            else:
                out.write("type={}; {} = {}\n".format(type(mark), mark, val))


#
# Test suite
#
if __name__ == "__main__":
    main()
