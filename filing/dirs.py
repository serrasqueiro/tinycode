#-*- coding: utf-8 -*-
# dirs.py  (c)2020  Henrique Moreira

"""
Listing directories
"""

# pylint: disable=no-self-use, missing-function-docstring

import os

UX_LETTER_FILE = "-"


class GenDir:
    """ Generic handle, with errors """
    _error = 0
    _path = ""
    upath = ""	# Universal path (no backslashes)
    _encoding = "UTF-8"
    _last_elem = None

    def is_ok(self) -> bool:
        return self._error == 0

    def slash(self) -> str:
        return "\\" if os.name == "nt" else "/"

    def get_path(self) -> str:
        if not self.upath:
            self.upath = simpler_path(self._path)
        return self.upath


class Dirs(GenDir):
    """ Dir listing """
    elements = list()
    paths = list()
    uxnames = list()

    def __init__(self, path=None, filter_in=None, filter_out=None):
        """ Constructor """
        self.elements, self.paths, self.uxnames = [], [], []
        if path:
            self._path = path
            self._scan_dir(path, filter_in, filter_out)


    def _scan_dir(self, path, filter_in, filter_out) -> int:
        """ Scan directory """
        apath = self.get_path()
        bpath = "" if apath == "." else apath
        elem = None
        for elem in os.scandir(apath):
            assert elem.name
            this = os.path.join(bpath, elem.name)
            letter = ux_letter(this)
            if letter == "d":
                path += self.slash()
            self.elements.append(elem.name)
            self.paths.append(this)
            self.uxnames.append(f"{letter} {this}")
        self._last_elem = elem
        return 0

    def rescan(self, path=None, filter_in=None, filter_out=None) -> list:
        """ Rescans directory. """
        if path:
            self._path = path
            self._scan_dir(path, filter_in, filter_out)
        return sorted(self.uxnames)

    def nodes(self, path=None) -> list:
        there = list()
        if path:
            self._path = path
        for elem in os.scandir(self.get_path()):
            there.append((elem.name, elem))
        return there

    def by_dir(self) -> list:
        there = list()
        for line in self.uxnames:
            if line[:2] == "d ":
                there.append(line[2:])
        return there

    def by_file(self) -> list:
        there = list()
        for line in self.uxnames:
            if line[:2] == f"{UX_LETTER_FILE} ":	# '- '
                there.append(line[2:])
        return there


def simpler_path(path) -> str:
    """ Returns a simpler path (and no backslashes!) """
    a_str = path.replace("\\", "/")
    while a_str.startswith("./"):
        a_str = a_str[2:]
    return a_str

def ux_letter(path) -> str:
    if os.path.isdir(path):
        letter = "d"
    elif os.path.islink(path):
        letter = "L"
    elif os.path.isfile(path):
        letter = UX_LETTER_FILE
    else:
        letter = "x"
    return letter


# Main script
if __name__ == "__main__":
    print("Import filing.dirs !")
