#-*- coding: utf-8 -*-
# repopath.py  (c)2021  Henrique Moreira

"""
github paths
"""

# pylint: disable=missing-function-docstring, no-self-use

HTTP_PATHS = {
    "git@github": "https://github.com/",
}


def main_test():
    """ Only for tests! """
    obj = GitHub("serrasqueiro/tinycode.git")
    https, gitpath = obj.paths()
    print("https url:   ", https)
    print("git ssh url: ", gitpath)
    new = obj.from_https(https)
    assert new
    print("SSH url:     ", new)
    assert new == gitpath
    assert obj.valid_domain()
    new = obj.from_ssh(gitpath)
    print("https url(2):", new)
    assert new == https
    print(f"""
Example:

import thunder.repopath
obj = thunder.repopath.GitHub("{obj.original_path()}")
print("https url:", obj.paths()[0])
""")


class GPath():
    """ Generic abstract path """
    def __init__(self, path=""):
        self._path = path

    def original_path(self) -> str:
        return self._path


class GitHub(GPath):
    """ Paths for GitHub """
    def __init__(self, path=""):
        super().__init__(path)
        self._user_domain = "git@github"
        self._at_domain = ""
        self._https, self._ssh_path = "", ""
        if path:
            self._set_from_path_name(path)

    def paths(self) -> tuple:
        """ Returns https and ssh access path pair. """
        return self._https, self._ssh_path

    def https(self) -> str:
        """ Returns https path.
        In case https path has no suffix '.git', this will arrange one
        (by using 'from_https()' function.
        """
        astr = self.from_ssh(self.from_https(self.paths()[0]))
        return astr

    def from_https(self, url:str) -> str:
        """ Returns ssh path """
        if not url.startswith("https://"):
            return ""
        if not url.endswith(".git"):
            url += ".git"
        tup = url[len("https://"):].split("/", maxsplit=1)
        if len(tup) < 2:
            return "?"
        self._at_domain, rest = tup
        assert self.valid_rest(rest), f"Invalid https: '{rest}'"
        astr = self._user_domain + ":/" + rest
        return astr

    def from_ssh(self, gitpath:str) -> str:
        """ Returns https path from gitpath """
        u_domain = self._user_domain + ":/"
        if not gitpath.startswith(u_domain):
            return ""
        rest = gitpath.split(u_domain, maxsplit=2)[1]
        url_start = HTTP_PATHS[self._user_domain]
        astr = url_start + rest
        return astr

    def _set_from_path_name(self, path:str, at_domain:str=""):
        """ Sets https and ssh path """
        assert path
        assert self.valid_rest(path), f"Invalid path: {path}"
        assert path.strip() == path
        self._at_domain = at_domain if at_domain else "github.com"
        self._https = f"https://{self._at_domain}/{path}"
        self._ssh_path = f"{self._user_domain}:/{path}"

    def valid_rest(self, url_path:str) -> bool:
        if not url_path or url_path.strip() != url_path:
            return False
        return ord(url_path[0]) > ord("/")

    def valid_domain(self) -> bool:
        """ Returns true if domain protected var is valid """
        return self.valid_rest(self._at_domain)


# Main script
if __name__ == "__main__":
    print("Import thunder.repopath !")
    main_test()
