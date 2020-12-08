#-*- coding: utf-8 -*-
# aliasnames.py  (c)2020  Henrique Moreira

"""
Listing files or names with Latin-1 chars, as ASCII.
"""

# pylint: disable=missing-function-docstring

import sys
from waxpage.redit import char_map
from filing.dirs import ADir, \
     joined_str

DEBUG = 0


def main_test():
    """ Just basic testing/ show class(es) usage. """
    args = sys.argv[1:]
    char_map.allow_symbols()
    for path in args:
        entries = ADir(path)
        names = Names(entries.elements, path)
        print("elements:\n{}".format(joined_str(names.basics(), "- ")))


class LatinMap():
    """ Mapping Latin-1 lettering """
    _amap = None

    def _new_map() -> dict:
        dct = {"to-ascii": dict(),
               "to-latin": dict(),
               }
        return dct

    def _new_hash(self, elem, astr) -> bool:
        self._amap["to-ascii"][elem] = astr
        self._amap["to-latin"][astr] = elem
        return True


class Names(LatinMap):
    """ Names in lists """
    name = ""
    listed = None

    """ Class handling equivalent names. """
    def __init__(self, listed, name=""):
        self.name = name
        self._set_list(listed)

    def basics(self) -> list:
        """ Returns listing using simplified ASCII names. """
        res = []
        self._hash_list(self.listed)
        for elem in self.listed:
            value = self._amap["to-ascii"].get(elem)
            if not value:
                value = elem
            res.append(value)
        return res

    def _set_list(self, listed, do_sort=True):
        assert isinstance(listed, (list, tuple))
        self.listed = sorted(listed, key=str.casefold) if do_sort else listed

    def _hash_list(self, alist, force_hash=False) -> bool:
        if self._amap and not force_hash:
            return False
        self._amap = LatinMap._new_map()
        for elem in alist:
            astr = simplified(elem)
            if elem != astr:
                self._new_hash(elem, astr)
        return True


def simplified(astr) -> str:
    assert isinstance(astr, str)
    newstr = astr
    while True:
        this = newstr.replace("  ", " ")
        if this == newstr:
            break
        newstr = this
    res = char_map.simpler_ascii(newstr)
    if DEBUG > 0:
        if res != newstr:
            print(''.join([f"{char_map.simpler_ascii(ch)}({ord(ch)}d)" for ch in newstr]))
    return res


# Main script
if __name__ == "__main__":
    print("Import filing.aliasnames !")
    main_test()
