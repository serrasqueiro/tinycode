# cub.py  (c)2018, 2020  Henrique Moreira (part of 'devcode')

"""
Cub of python vars and classes

Compatibility: python 3.
"""

# pylint: disable=unused-argument

#_REPO = "https://github.com/serrasqueiro/tinycode/"
_VERSION = "1.00"


def main_test() -> bool:
    """ Just a basic test """
    # pylint: disable=possibly-unused-variable, import-outside-toplevel
    sample1 = "hello"
    _sample2 = "world"
    pic = PiClass()
    npro = non_protected()
    loc = non_protected(locals())
    print(f"globals(), non_protected(): {npro}")
    print(f"non_protected(locals()): {loc}")
    assert "sample1" in loc
    # with ZipFile('playlists.zip') as zipf:
    #   print('\n'.join([name if not name.startswith("_") else "" for name in dir(zipf)]))
    dir_dot = dir('.')
    alist = [name if not name.startswith("_") else None for name in dir_dot]
    print("dir('.'):", '; '.join(non_empty(alist)))
    #print(f"dir('.'): {join_str(non_protected(dir_dot), ';')}")
    #print("private() from main_test() function:", private(dir(main_test)))
    assert "__name__" in private(dir(main_test))
    print("Global constants:", '; '.join(constants()))
    print("Constants, global:", constants_dict())
    pi_vars = constants(dir(pic))
    assert isinstance(pi_vars, list)
    print("Instance 'pic' vars:", pi_vars)
    assert pi_vars == constants(dir(PiClass))
    print("members_of(pic):", members_of(pic))
    print("members_dict(pic):", members_dict(pic))
    if pic.value() >= 3.14:
        return True
    import waxpage.redit
    module_vars = vars(waxpage.redit)
    for key, val in module_vars.items():
        print("key:", key, val if not isinstance(val, dict) else dict_keys(val.keys()))
    return False


class PiClass():
    """ Sample class """
    # pylint: disable=no-self-use
    _BASIC_CONSTANT_PI = 3.14
    name = ""

    def value(self):
        """ Returns a basic constant: approximate value of PI """
        return PiClass._BASIC_CONSTANT_PI


def dict_keys(dct_keys) -> list:
    """ Returns a sorted list of dictionary keys """
    res = sorted(list(dct_keys))
    return res


def is_constant(name) -> bool:
    """ Returns True is name expresses a constant Python name """
    assert isinstance(name, str)
    isconst = name.replace("_", "").isupper()
    # https://github.com/PyCQA/pylint/blob/fde732e0e9a4f224c5ae48ad942c6d955aa0a8e6/pylint/checkers/base.py#L128
    return isconst


def constants(dct=None) -> list:
    """ Returns the list of constants """
    res = list()
    what = globals() if dct is None else dct
    for key in what:
        if is_constant(key):
            res.append(key)
    return sorted(res)


def constants_dict(dct=None) -> dict:
    """ Returns the value pair (name, value) for all (dct) constants """
    values = dict()
    what = globals() if dct is None else dct
    for key in what:
        if is_constant(key):
            values[key] = what[key]
    return values


def private(dct=None) -> list:
    """ Returns a list of private vars """
    res = list()
    what = globals() if dct is None else dct
    for key in what:
        if key.startswith("__"):
            res.append(key)
    return res


def non_protected(dct=None) -> list:
    """ Returns a list of unprotected vars/ functions """
    res = list()
    what = globals() if dct is None else dct
    for key in what:
        if not key.startswith("_"):
            res.append(key)
    return sorted(res)


def non_empty(alist) -> list:
    """ Returns a list, except 'None' elements """
    res = list()
    for elem in alist:
        if elem is not None:
            res.append(elem)
    return res


def members_of(inst) -> list:
    """ Returns the member names of a class """
    res = [attr for attr in dir(inst)
           if not callable(getattr(inst, attr)) and not attr.startswith("__")]
    return res


def members_dict(inst) -> dict:
    """ Returns the member names of a class """
    values = dict()
    for attr in dir(inst):
        if not callable(getattr(inst, attr)) and not attr.startswith("__"):
            values[attr] = getattr(inst, attr)
    return values


def join_str(alist, sep="\n"):
    """ Joined string from list """
    astr = ""
    for elem in alist:
        if not elem:
            continue
        astr += elem
        astr += sep
    return astr


#
# Test suite
#
if __name__ == "__main__":
    assert main_test()
