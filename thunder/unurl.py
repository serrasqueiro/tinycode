#-*- coding: utf-8 -*-
# unurl.py  (c)2021  Henrique Moreira

""" unquote complicated URLs
"""

# pylint: disable=missing-function-docstring, no-self-use

import sys
import urllib.parse

SAMPLE_HTTPS = "https://example.com/"

SPECIFIC_SIMPLER = {
    "sharepoint.com/": {
        "nick": [
            ("?RootFolder=", "sharepoint/.../")
            ]
    },
}


def main_test():
    """ Only for tests! """
    tiny_test(sys.argv[1:])

def tiny_test(args):
    param = args
    astr = ' '.join(param)
    uno = UrlLink(astr)
    markdown = f'[here]({uno.markdown()})'
    print(str(uno) + "\n\nSimple:", markdown, end="\n\n")


class UrlLink():
    """ URL links, simplified """
    def __init__(self, astr:str=SAMPLE_HTTPS):
        self._url = ""
        self._start(astr)

    def markdown(self) -> str:
        """ Returns a markdown compatible string """
        return self._markdown

    def _start(self, astr:str) -> bool:
        unq = urllib.parse.unquote(astr)
        to_what, akey = None, ""
        for key in sorted(SPECIFIC_SIMPLER):
            chk = "." + key
            if chk in unq:
                to_what, akey = SPECIFIC_SIMPLER[key], key
                break
        self._url = unq
        new = unq.split("https://", maxsplit=1)[-1]
        self._markdown = new
        if not to_what:
            return True
        assert akey
        for nick_a, nick_b in to_what["nick"]:
            pos = new.find(nick_a)
            if pos >= 0:
                suffix = new[pos + len(nick_a):]
                if nick_b.endswith("/") and suffix.startswith("/"):
                    suffix = suffix[1:]
                new = nick_b + suffix
        self._markdown = new
        return True

    def _markdown_str(self, astr:str) -> str:
        if "(" in astr or ")" in astr:
            return astr.replace("(", "%40").replace(")", "%41")
        return astr

    def __str__(self) -> str:
        return self._url


# Main script
if __name__ == "__main__":
    print("Import thunder.unurl !")
    main_test()
