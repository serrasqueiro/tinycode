# giturled.py  (c)2020  Henrique Moreira (part of 'waxpage')

"""
Change git url from repo
"""

# pylint: disable=unused-argument


import sys
import os

SAMPLE_URL="https://github.com/serrasqueiro/prizedseason.git"
SAMPLE_SSH="git@github.com:serrasqueiro/prizedseason.git"


def main():
    """ Main test script! """
    prog = __file__
    code = main_run(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} url [repo] [repo ...]

Where url is e.g.
	{SAMPLE_URL}
""")
    sys.exit(code if code else 0)


def main_run(out, err, args):
    """ Main run """
    opts = {"what": "github",
            }
    if not args:
        return None
    url = args[0]
    param = args[1:]
    if url.startswith("https://"):
        if not param:
            param = [os.getcwd()]
        code = show_conv_to_ssh(out, err, url, param, opts)
    else:
        return None
    return code


def show_conv_to_ssh(out, err, url, param, opts):
    """ Show conversion from https to ssh url in git (github) """
    for name in param:
        matches = 0
        subm = os.path.join(name, ".gitmodules")
        if os.path.isfile(subm):
            other = os.path.join(name, ".git/config")
            n_match, _, listed = lined_url(other, url, opts)
            matches += n_match
            if n_match == 1:
                print(f"# Substituting config: {other}")
                with open(other, "w") as othout:
                    othout.write("\n".join(listed)+"\n")
            # Now .gitmodules itself!
            n_match, _, listed = lined_url(subm, url, opts, hints=True)
            if not n_match:
                err.write(f"Not found: {url}\n")
                return 2
            if n_match > 1:
                err.write(f"Too many matches: {url}\n")
                return 3
            matches += n_match
            print(f"# Substituting submodules list: {subm}")
            with open(subm, "w") as newout:
                newout.write("\n".join(listed)+"\n")
        if matches:
            print(f"# Changes: {matches}")
            if matches and matches != 2:
                err.write(f"Warning: {matches} substitutions found (not 2)\n")
    return 0


def lined_url(path, url, opts, hints=False) -> tuple:
    """ Returns the matched lines """
    idx = 0
    n_match, matched, listed = 0, list(), list()
    what = opts["what"]
    parts = url.split("github.com/", maxsplit=1)[1].split("/")
    username = parts[0]
    repo = parts[1].rstrip("/")
    assert repo
    if repo.endswith(".git"):
        atdir = repo[:-len(".git")]
    else:
        atdir = repo
    if what == "github":
        newer = f"git@github.com:{username}/{repo}"
    else:
        newer = None
    assert newer
    with open(path, "r") as reader:
        for line in reader.read().splitlines():
            idx += 1
            there = 0
            u_str = f"url = {url}"
            if line.strip() == u_str:
                there = idx
                n_match += 1
                new_str = line.replace(url, newer)
            else:
                new_str = line
            matched.append(there)
            listed.append(new_str)
    if hints:
        if n_match <= 1:
            print(f"cd {atdir}; git remote set-url origin {newer}")
    return n_match, matched, listed


#
# Test suite
#
if __name__ == "__main__":
    main()
