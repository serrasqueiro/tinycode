#-*- coding: utf-8 -*-
# bird.py  (c)2020  Henrique Moreira

"""
Thunderbird profiles
"""

# pylint: disable=no-self-use, missing-function-docstring

import os
import filing.dirs
from filing.dirs import dprint
from thunder.profkind import Profile


def main_test():
    """ Only for tests! """
    filing.dirs.DEBUG = 1
    #apath = "/tmp/profiles.ini"
    apath = ""
    bird = Bird(apath)
    for key, alist in bird.keying():
        ori_key = bird.workspace()["all"].original_key(key)
        print(ori_key)
        print(" " * 3, alist, end="\n\n")


class Bird():
    """ Bird -- Thunderbird profiles """
    def __init__(self, path=""):
        self._workspace = thunderbird_profile(path)

    def workspace(self) -> dict:
        """ Returns the Thunderbird 'workspace' """
        return self._workspace

    def keying(self) -> list:
        """ Returns workspace, ordered by key """
        aprof = self._workspace["profile"]
        return [(key, aprof[key]) for key in aprof["[keys]"]]


def thunderbird_profile(path:str="") -> dict:
    """ Best-effort find of thunderbird profile.
    Returns a dictionary with understandable profiles.
    All paths are in Unix-style ('/', rather than backslashes!)
    """
    # User at: C:/Users/$USER/AppData/Roaming/Thunderbird/profiles.ini
    appdata = os.environ.get("APPDATA")
    if appdata:
        appdata = appdata.replace("\\", "/").strip("/") + "/"
    else:
        appdata = os.environ["HOME"] + "/."
    appdata += "thunderbird" if is_unix() else "Thunderbird"
    profs = appdata + "/profiles.ini"
    if path:
        profs = path
    dprint("tpf", f"thunderbird_profile('{path}')={profs}")
    aprof = Profile(profs)
    res = {
        "profile": aprof.profile(),
        "all": aprof,
    }
    return res

def is_unix() -> bool:
    return os.name != "nt"

# Main script
if __name__ == "__main__":
    print("Import thunder.bird !")
    main_test()
