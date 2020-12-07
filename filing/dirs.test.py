#-*- coding: utf-8 -*-
# dirs.test.py  (c)2020  Henrique Moreira

"""
Listing directories
"""

# pylint: disable=no-self-use, missing-function-docstring

import sys
import filing.dirs as dirs
from filing.dirs import joined_str

PRE = "-"


def main_test():
    """ Main (minimalist) test """
    is_ok = run_test(sys.argv[1:])
    assert is_ok


def run_test(args) -> bool:
    """ Run test: if user has not chosen any args, you are assuming basic a test """
    is_ok = _class_tests()
    assert is_ok
    if args:
        if args[0] == "@basic":
            return _basic_test()
        for apath in args:
            is_ok = _test_dirs(apath, len(args))
    else:
        apath = "."
        is_ok = _test_dirs(apath, -1)
    return is_ok


def _class_tests() -> bool:
    """ Basic class tests """
    # pylint: disable=protected-access
    a_sort = dirs.GenDir._alpha_sort
    assert len(a_sort) >= 3
    alphas = a_sort[0]
    assert len(alphas) == 26
    one = dirs.Dirs(".")
    two = dirs.Dirs()
    hdot = dirs.HomeDotFiles()
    dir_list = sorted(hdot.by_dir())
    files_list = sorted(hdot.by_file())
    print("""HomeDotFiles().by_dir()
{}-- .by_files() --
{}<<< - HomeDotFiles() end.
""".
          format(joined_str(dir_list, " ~ "),
                 joined_str(files_list, " ~ ")))
    is_ok = one._alpha_sort == two._alpha_sort
    assert is_ok
    names = hdot.by_name()
    xtra_info = f" (upath='{hdot.get_path()}')"
    if ".bashrc" in names:
        print(f".bashrc exists in your home: {dirs.home_path()}{xtra_info}")
    else:
        print("No .bashrc at your home")
    dirs.dprint('dir', "dot files names, ordered:", names)
    print()
    return True


def _basic_test() -> bool:
    """ Basic dir test on current directory """
    entries = dirs.Dirs(".", filter_in=("*.py", "dirs.py"), filter_out="_*")
    #	...or ... entries = dirs.Dirs(".", filter_in=("*.py", "dirs.py"), filter_out=("_*",))
    print("Relevant Python files on current dir ({}):\n{}\n".
          format(dirs.get_current_directory(),
                 entries.elements))
    assert "__init__.py" not in entries.elements
    print("Checking exclusions:")
    for excl in (tuple(),
                 ("__*",),
                 ):
        is_ok = _run_basic_test(excl)
        assert is_ok
    return True


def _run_basic_test(excl) -> bool:
    entries = dirs.Dirs(dirs.CUR_DIR, filter_out=excl)
    print("#entries.by_dir()={}, #entries.by_file()={}, entries.uxnames:\n{}".
          format(len(entries.by_dir()),
                 len(entries.by_file()),
                 joined_str(entries.uxnames, PRE)))
    there_excl = entries.get_filters()["excl"]
    s_text = "no exclusions" if there_excl == tuple() else "with exclusions"
    print("Include/ Exclude filter:", entries.get_filters(),
          f"; {s_text}")
    assert entries.get_filters()["excl"] == excl
    return True


def _test_dirs(apath, num_args) -> dirs.Dirs:
    assert num_args >= -1
    if apath == "@empty":
        apath = ""
    extra = "_*.py"	# exclude every python file starting with an underscore ('_')
    extra_2 = "*~"	# exclude any (Linux) backup file
    check = dirs.Dirs(apath, filter_out=(extra, extra_2, "__pycache__", "__init__.py"))
    print("check.by_dir():", check.by_dir())
    last_elems = None
    for idx in (1, 2,):
        if idx > 1:
            check.rescan()
        print(f"Iteration {idx}, check.uxnames:")
        print(joined_str(check.uxnames, PRE))
        print(f"check.elements: {check.elements}\n")
        for name in check.elements:
            assert not name.startswith("_")
        if last_elems:
            assert last_elems == check.elements
        last_elems = check.elements
    new = dirs.ADir(apath, filter_out="*~")
    names = new.by_name()
    print(f"Names at '{apath}':\n{joined_str(names)}")
    latins = new.get_by("latin")
    print("ADir get_by('latin') -->", latins)
    print(f"latin_sort()={new.latin_sort()}")
    return check


# Main script
if __name__ == "__main__":
    main_test()
