# cvs_touch.py  (c)2021  Henrique Moreira

"""
cvs_touch - Touch local CVS repository files (checkedout)

Compatibility: python 3.
"""

# pylint: disable=unused-argument, missing-function-docstring, no-self-use

import sys
import re
import os.path
import datetime
from waxpage.uxdate import \
     date_from_cvs_entry_str, \
     date_from_cvs_v_format, \
     posix_touch, \
     basic_date

DEF_IN_CODE = "ISO-8859-1"
DEF_GETTER = {
    "verbose": 0,
    }
COLLECTOR_LEVEL_MAX = 100

NO_DATE = datetime.date(1970, 1, 1)


def main():
    """ Main script! """
    prog = __file__
    code = runner(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} [options] path [path ...]

Options are:
   -v          Verbose mode
""")
    sys.exit(code if code else 0)


def runner(out, err, args) -> int:
    """ Main run """
    verbose = 0
    param = args
    opts = {
        "verbose": 0,
        "dump": 1,
        "recurse": 0,
        "_max_level": 0,
    }
    while param and param[0].startswith("-"):
        if param[0] in ("-v", "--verbose"):
            del param[0]
            opts["verbose"] += 1
            continue
        if param[0] in ("-r", "--recurse"):
            del param[0]
            opts["recurse"] = 1
            continue
        return None
    if not param:
        print("Do you mean '.' ?\n")
        return None
    invs = [opt for opt in param if opt.startswith("-")]
    if invs:
        print("Invalid paths:", invs)
        print()
        return None
    if opts["recurse"]:
        opts["_max_level"] = COLLECTOR_LEVEL_MAX
    code = collector(out, err, param, opts)
    return code


def collector(out, err, args, opts) -> int:
    """ Collects from CVS local repo """
    assert err
    for path in args:
        if not os.path.isdir(path):
            err.write(f"Not a directory: {path}\n")
            return 2
    for path in args:
        code = do_collect(out, err, path, opts)
        if code != 0:
            if code <= -1:
                shown = str(opts["_max_level"])
                err.write(f"Max. recursion achieved: {shown}\n")
            return code
    return 0


def do_collect(out, err, path, opts, level=0):
    dbg = 1 if opts["verbose"] else 0
    cinfo = cvs_info(path)
    if cinfo is None:
        err.write(f"Collect failed for: {path}\n")
        return 3
    _, _, listing = cinfo
    handles = getter(None, err, cinfo, path, opts)
    cinfo, entries = handles
    if entries is None:
        err.write(f"Bailing out for: {path}\n")
        return 2
    for entry in entries:
        if opts["dump"]:
            print(entry)
    path_root, path_rel = cinfo[1]
    cvs_path = os.path.join(path_root, path_rel)
    is_ok = touch_files(out, err, cvs_path, entries, debug=dbg)
    if not is_ok:
        err.write(f"Skipped: {path}\n")
        return 1
    if opts["recurse"]:
        if level >= opts["_max_level"]:
            return -1
        dir_list = listing["dirs"]
        for adir in dir_list:
            assert adir.startswith("/")
            newdir = os.path.join(path, adir[1:])
            do_collect(out, err, newdir, opts, level+1)
    return 0


def touch_files(out, err, cvs_path, entries, debug=0) -> bool:
    """ Touch files known to a CVS repository
    """
    # ...all or nothing
    assert err
    there, absent = list(), list()
    for entry in entries:
        atpath = os.path.join(cvs_path, entry.path)
        vpath = f"{atpath},v"
        if os.path.isfile(vpath):
            there.append((vpath, entry))
        else:
            absent.append(entry.path)
    if absent:
        return False
    for vpath, entry in there:
        if debug > 0:
            print("Reading:", vpath, "at:", entry.directory())
        lines = RCSContent(vpath).lines
        pname = os.path.join(entry.directory(), entry.path)
        is_ok, msg = cvs_touch_file(out, pname, lines)
        xtra = f" {msg}" if msg else ""
        if is_ok:
            if out:
                out.write(f"Touched: {pname}{xtra}\n")
        else:
            xtra = " (RCS!)" if msg.startswith("Strange-RCS") else ""
            if not xtra:
                if not os.path.isfile(xtra):
                    xtra = " (file not there)"
            err.write(f"Cannot touch: {pname}{xtra}\n")
    return True

def cvs_touch_file(out, pname, lines) -> bool:
    """ Touch the file.
    """
    #print(f"cvs_touch_file({pname}, #lines={len(lines)})")
    first = lines[0]
    spl = re.split("\t|;$", first)
    assert len(spl) == 3
    head, version, empty = spl
    assert not empty
    assert head == "head"
    cont = after_blank(lines)
    line_version = cont[0]
    assert version == line_version
    date_etc = cont[1].split("\t")
    if date_etc[0] != "date":
        return False, f"Strange-RCS={pname}"
    vdate = date_etc[1].rstrip(";")
    dttm = date_from_cvs_v_format(vdate)
    is_ok = posix_touch(pname, dttm)
    if not is_ok:
        return is_ok, f"File touch failed: {pname}"
    return True, basic_date(dttm)


def getter(out, err, cinfo, path, opts=None) -> tuple:
    """ Info from all listed files. """
    entries = list()
    _, parts, listing = cinfo
    repo_dir = os.path.join(parts[0], parts[1])
    if not os.path.isdir(repo_dir):
        err.write(f"Cannot find CVS repo dir: {repo_dir}\n")
        return (None, None)
    for entry in listing["files"]:
        entries.append(CVSEntryDesc(entry, path))
    res = (cinfo, entries)
    if not out:
        return res
    for entry in listing["dirs"] + listing["files"]:
        ced = CVSEntryDesc(entry)
        out.write(f"{ced}\n")
    return res


def cvs_info(path):
    """ Returns CVS local information, under 'path'/CVS/ """
    cvs_str = "CVS"
    listing = {"dirs": list(), "files": list()}
    prefix = os.path.join(path, cvs_str) if path else cvs_str
    root, repo = os.path.join(prefix, "Root"), os.path.join(prefix, "Repository")
    entries = os.path.join(prefix, "Entries")
    all_ok = os.path.isfile(root) and os.path.isfile(repo)
    if not all_ok:
        return None
    with open(root, "r") as fd_1:
        lines = fd_1.readlines()
    assert len(lines) == 1
    parts = [lines[0].strip()]
    with open(repo, "r") as fd_2:
        lines = fd_2.readlines()
    assert len(lines) == 1
    parts += [lines[0].strip()]
    with open(entries, "r") as fd_3:
        lines = fd_3.readlines()
    for s_item in lines:
        item = s_item.strip()
        if not item:
            continue
        if item[0] == "D":
            if item != "D":
                adir = item[1:].rstrip('/')
                assert adir
                listing["dirs"].append(adir)
        else:
            listing["files"].append(item)
    res = (
        (root, repo, entries),
        parts,
        listing
        )
    return res


class CVSEntryDesc():
    """ CVS Entry Description """
    def __init__(self, astr, adir=None):
        self._adir = adir
        self.path, self.version, self.adate, stk = CVSEntryDesc._set_from_str(astr)
        self.sticky = stk if stk else ""
        self.date = NO_DATE
        self._set_date()
        assert self.valid()

    def valid(self) -> bool:
        for achr in "',":
            if achr in self.path:
                return False
        return True

    def directory(self) -> str:
        astr = self._adir
        assert astr is not None
        return astr

    @staticmethod
    def _set_from_str(astr) -> tuple:
        # Format example: /fname/1.2/Sat Feb 13 21:29:59 2021//
        # Same as:	date +"%a %b %d %H:%M:%S %Y" (--date="2021-02-13 21:29:59")
        # Another sample: /RENE_20190321_2018T4.zip/1.1/Sun Jul 14 10:50:42 2019/-kb/
        assert isinstance(astr, str)
        version, adate, stk = "(dir)", None, None
        if astr[0] == "D":
            path = astr[1:].split('/')[1]
            return (path, version, adate, stk)
        assert astr[0] == "/"
        assert astr.endswith("/")
        new = astr[1:-1]
        path, version, adate, stk = new.split('/')
        return (path, version, adate, stk)

    def _set_date(self) -> bool:
        if not self.adate:
            return False
        self.date = date_from_cvs_entry_str(self.adate)
        return True

    def __str__(self) -> str:
        """ Return string like element """
        return self.to_string()

    def to_string(self, quoted=False) -> str:
        s_quote = "'" if quoted else ""
        s_date = basic_date(self.date) if self.adate else ""
        desc = f":{self.version}:{s_quote}{s_date}{s_quote}" if self.adate else "/"
        astr = f"{s_quote}{self.path}{s_quote}{desc}"
        return astr


    def __repr__(self) -> str:
        """ Return string like element """
        return self.to_string(quoted=True)

class RCSContent():
    """ RCS file (,v) - for CVS """
    def __init__(self, vpath, enc=None):
        assert isinstance(vpath, str)
        self._vpath = vpath
        self.lines = self._reader(vpath, enc if enc else DEF_IN_CODE)

    def _reader(self, vpath, enc):
        """ Reads an RCS (,v) file """
        lines = [line.rstrip() for line in open(vpath, "r", encoding=enc).readlines()]
        return lines

    def get_path(self) -> str:
        return self._vpath


def after_blank(alist) -> list:
    """ Returns the list after the last blank. """
    idx = 0
    while idx < len(alist):
        if alist[idx] == "":
            idx += 1
            for item in alist[idx:]:
                if item:
                    return alist[idx:]
                idx += 1
        idx += 1
    assert False
    return list()


# Main script
if __name__ == "__main__":
    main()
