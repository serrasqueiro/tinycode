#-*- coding: utf-8 -*-
# profkind.py  (c)2020  Henrique Moreira

"""
Thunderprofkind profiles
"""

# pylint: disable=no-self-use

class Profile():
    """ Profile kind textual handler """
    _profile = None

    def __init__(self, path:str="", data:str=""):
        self._profile = parse_text(text_reader(path) + data)

    def profile(self) -> dict:
        """ Returns the entire profile! """
        return self._profile

    def original_key(self, name:str) -> str:
        """ Returns the original key-name.
        E.g. for the original key name ['General'],
        the key stored is 'general'.
        This method returns the original name 'General'!
        """
        return self._profile["[original-keys]"][name]

def text_reader(path:str) -> str:
    """ Returns the string of a file, if path != '', always '\n' at the end.
    """
    if not path:
        return ""
    data = open(path, "r").read()
    if not data.endswith("\n"):
        data += "\n"
    return data

def parse_text(data:str) -> dict:
    """ Returns a dictionary with the keywords found.
    Keywords are embraced by '[' and ']', e.g. '[General]'.
    """
    res = {
        "[keys]": [],
        "[original-keys]": dict(),
    }
    pre = [line.strip() for line in data.splitlines()]
    last = ""
    for line in pre:
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            key = line[1:-1].strip()
            akey = valid_key(key)
            assert akey, f"Invalid key: '{key}'"
            last = akey
            assert akey not in res["[original-keys]"]
            res["[keys]"].append(akey)
            res["[original-keys]"][akey] = key
            continue
        if last:
            key = last
        else:
            key = "[]"
        if key not in res:
            res[key] = []
        if "=" in line:
            ids = [aval.strip() for aval in line.split("=", maxsplit=1)]
            ids = tuple(["="] + ids)
        else:
            ids = [line]
        res[key].append(ids)
    return res

def valid_key(key:str) -> str:
    """ Returns True if string 'key' is a valid key for '[Key]'... """
    last = " "
    if not key:
        return ""
    for achr in key:
        if achr == " ":
            if last == " ":
                return ""	# No two consecutive blanks!
            last = achr
            continue
        if not achr.isalnum():
            return ""
        last = achr
    return key.lower().replace(" ", "-")


# Main script
if __name__ == "__main__":
    print("Import thunder.profkind !")
