#-*- coding: utf-8 -*-
# dirs.py  (c)2020  Henrique Moreira

"""
Listing directories
"""

# pylint: disable=no-self-use, missing-function-docstring

import os

DEBUG = 0	# define 1 if you want to see debug
UX_LETTER_FILE = "-"
CUR_DIR = (".",)


class GenDir:
    """ Generic handle, with errors """
    _error = 0
    _path = ""
    upath = ""	# Universal path (no backslashes)
    _encoding = "UTF-8"
    _last_elem = None
    _filters = None
    _alpha_sort = ("abcdefghijklmnopqrstuvwxyz", "0", "@",)

    def is_ok(self) -> bool:
        return self._error == 0

    def slash(self) -> str:
        return "\\" if os.name == "nt" else "/"

    def get_path(self) -> str:
        if not self.upath:
            self.upath = simpler_path(self._path)
        return self.upath

    def get_filters(self):
        return self._filters


class Dirs(GenDir):
    """ Dir Scan (and listing) """
    elements = list()
    paths = list()
    uxnames = list()

    def __init__(self, path=None, filter_in=None, filter_out=None):
        """ Constructor """
        self._init_dirs(path, filter_in, filter_out)

    def rescan(self, path=None, filter_in=None, filter_out=None) -> list:
        """ Rescans directory. """
        self._init_lists()
        if filter_in is not None or filter_out is not None:
            is_ok = self._set_filters(filter_in, filter_out)
            assert is_ok
        if path:
            self._path = path
        else:
            path = self._path
        if path:
            self._scan_dir(path, self._filters)
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

    def _init_dirs(self, path, filter_in, filter_out):
        is_ok = False
        self._init_lists()
        self._set_path(path)
        is_ok = self._set_filters(filter_in, filter_out)
        assert is_ok
        if self._path:
            self._scan_dir(self._path, self._filters)
        else:
            self.elements, self.paths, self.uxnames = [], [], []
            self._last_elem = None

    def _init_lists(self):
        self.elements, self.paths, self.uxnames = [], [], []

    def _set_path(self, path) -> bool:
        self._path = None
        if isinstance(path, str):
            self._path = path
        elif isinstance(path, tuple):
            is_ok = path == CUR_DIR
            if is_ok:
                self._path = get_current_directory()
        if not self._path:
            return False
        return True

    def _set_filters(self, filter_in, filter_out) -> bool:
        include = ("*",) if filter_in is None else tups_from_filter(filter_in)
        exclude = tups_from_filter(filter_out)
        if not include:
            include = ("",)
        if not exclude:
            exclude = tuple()
        dct = {"incl": include,
               "excl": exclude,
               }
        self._filters = dct
        return True

    def _scan_dir(self, path, filters) -> int:
        """ Scan directory """
        assert filters is None or isinstance(filters, dict)
        apath = self.get_path()
        bpath = "" if apath == "." else apath
        elem, one = None, None
        for elem in os.scandir(apath):
            assert elem.name
            this = os.path.join(bpath, elem.name)
            dcode = user_show_entry(self._filters, elem.name, this)
            if dcode != 1:
                continue
            one = elem
            letter = ux_letter(this)
            if letter == "d":
                path += self.slash()
            self.elements.append(elem.name)
            self.paths.append(this)
            self.uxnames.append(f"{letter} {this}")
        self._last_elem = one
        return 0


class ADir(Dirs):
    """ ADir is similar to 'Dirs' class, except it allows sorting,
        and changing current directory to the required dir.
    """
    _latin_sort = dict()

    def _init_adir(self, path, filter_in, filter_out):
        assert path
        keep = get_current_directory()
        os.chdir(path)
        self._init_dirs(".", filter_in, filter_out)
        if keep:
            os.chdir(keep)

    def by_name(self):
        names = self._latin_sort.get("@names")
        if not names:
            self._latin_sort = {
                "@names": None,
                "@dirs": list(),
                "@file": list(),
                }
            self._order_by_name(self._latin_sort)
        dprint('dir',
               "Latin sort:", list(self._latin_sort.keys()))
        names = self._latin_sort["@names"]
        assert names
        return names

    def _order_by_name(self, dct) -> bool:
        for uxname in self.uxnames:
            what, name = uxname[0], uxname[2:]
            assert name != "."
            if not name:
                continue
            if what == "d":
                dct["@dirs"].append(name + "/")
            else:
                dct["@file"].append(name)
        dct["@dirs"].sort(key=str.casefold)
        dct["@file"].sort(key=str.casefold)
        dct["@names"] = dct["@dirs"] + dct["@file"]
        return True


class HomeDotFiles(ADir):
    """ Home files starting with dot (.*) """
    def __init__(self, path=None):
        # pylint: disable=super-init-not-called
        if path is None:
            path = home_path()
        outs = (".saves-*",
                ".*.old",
                )
        self._init_adir(path, ".*", filter_out=outs)


def simpler_path(path) -> str:
    """ Returns a simpler path (and no backslashes!) """
    astr = path.replace("\\", "/")
    last = astr
    while len(astr) > 2:
        if astr.endswith("//"):
            astr = astr[:-1]
        if astr == last:
            break
        last = astr
    while astr.startswith("./"):
        astr = astr[2:]
    return astr


def ux_letter(path) -> str:
    """ Unix-like letter;
        Note: 'L' (upper-case L) mark soft-links, rather than 'l')
    """
    if os.path.isdir(path):
        letter = "d"
    elif os.path.islink(path):
        letter = "L"
    elif os.path.isfile(path):
        letter = UX_LETTER_FILE
    else:
        letter = "x"
    return letter


def tups_from_filter(afilter) -> tuple:
    if isinstance(afilter, list):
        alist = afilter
    elif isinstance(afilter, tuple):
        alist = list(afilter)
    elif isinstance(afilter, str):
        alist = tups_from_filter(afilter.split(";"))
    elif afilter is None:
        alist = list()
    else:
        assert False
    words = list()
    wilds = list()
    has_wild = False
    for tup in alist:
        if not isinstance(tup, str):
            return tuple()
        if not tup:
            continue	# empty strings not added
        if tup == "*":
            if has_wild:
                continue	# no '*' wild-card duplicates
            has_wild = True
        if "*" in tup:
            if tup not in wilds:
                wilds.append(tup)
        elif tup not in words:
            words.append(tup)
    if has_wild:
        return ("*",)
    words.sort()
    wilds.sort()
    tups = tuple(words + wilds)
    return tups


def user_show_entry(dfilter, name, path, by_name=True, simple_in=False):
    """ Wrapper to modify for who is using this module, if needed.
    """
    #simple_in = True	# ... or False
    dcode = do_show_entry(dfilter, name, path, by_name, simple_in)
    assert dcode >= -1
    return dcode


def do_show_entry(dfilter, name, path=None, by_name=True, simple_in=False) -> int:
    """ Returns 1 if name is to be shown;
        0 if name is not in the inclusion list;
        -1 if name is in the exclusion list.
    """
    incl = dfilter["incl"]
    excl = dfilter["excl"]
    if path is None:
        apath = name
    else:
        apath = path
    if by_name:
        apath = name
    # Check if is included first
    if simple_in:
        dcode = int(apath in incl or incl == ("*",))
        dprint('dir',
               f"Debug: dcode={dcode}, path={apath}, incl={soft_filter(incl)}", "(simple_in)")
    else:
        match = is_within_filter(apath, incl)
        dcode = 1 if match else 0
        dprint('dir',
               f"Debug: dcode={dcode}, path={apath}, pattern='{match}', incl={soft_filter(incl)}")
    if dcode != 1:
        return 0
    # Check if it is in the exclusion list
    if not excl:
        return 1	# Exclusion list is empty
    excluded = excl == ("*",)
    if excluded:
        return -1
    match = is_within_filter(apath, excl)
    dcode = -1 if match else 1
    dprint('dir',
           f"Debug: dcode={dcode}, path={apath}, match='{match}', excl={soft_filter(excl)}")
    return dcode


def soft_filter(afilter) -> str:
    if isinstance(afilter, str):
        return afilter
    res = ";".join(afilter)
    return res


def is_within_filter(name, afilter) -> str:
    """ Returns an empty string if name not within the 'afilter'.
        Or the matching filter pattern found.
    """
    assert isinstance(name, str)
    assert isinstance(afilter, (list, tuple))
    if not name:
        return ""
    for one in afilter:
        if one == "*":
            return one
        pos = one.find("*")
        if pos == -1:
            if name == one:
                return name
        left = one[:pos]
        right = one[pos+1:]
        is_ok = True
        if left:
            is_ok = name.startswith(left)
        if not is_ok:
            continue
        if right:
            is_ok = name.endswith(right)
        if is_ok:
            return one
    return ""


def joined_str(alist, pre="", post="\n") -> str:
    astr = ""
    for elem in alist:
        astr += f"{pre}{elem}{post}"
    return astr


def get_current_directory() -> str:
    res = os.getcwd()
    return res


def home_path() -> str:
    """ Return the home path, in slash-notation """
    if os.name == "nt":
        home = os.environ.get("USERPROFILE")
    else:
        home = os.environ.get("HOME")
    if not home:
        return ""
    astr = home.replace("\\", "/")
    return astr


def dprint(what, *rest) -> bool:
    if not DEBUG:
        return False
    assert what == 'dir'
    #astr = "{}".format('+'.join(rest))
    print(*rest)
    return True


# Main script
if __name__ == "__main__":
    print("Import filing.dirs !")
