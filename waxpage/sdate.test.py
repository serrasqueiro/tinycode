# sdate.test.py  (c)2020  Henrique Moreira (part of 'waxpage')

""" Test 'sdate' module
"""

# pylint: disable=missing-function-docstring

import sys
import os
import waxpage.sdate as sdate


def main():
    """ Main test script! """
    prog = __file__
    code = test_sdate_test(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog} [filename|--date] [...]
""")
    sys.exit(code if code else 0)


def test_sdate_test(out, err, args) -> int:
    """ Main module test! """
    assert out
    assert err
    param = args
    if not param:
        param = ["--date"]
    code = run_sdate(param)
    assert code == 0
    return code


def run_sdate(param) -> int:
    for name in param:
        if name == "--date":
            return test_date(param[1:])
        path = name
        test_date([path])
    return 0


def test_date(param) -> int:
    if not param:
        now = sdate.current()
        dump_dates(now)
        return 0
    for name in param:
        try:
            astat = os.stat(name)
        except FileNotFoundError:
            astat = None
        shown = "" if astat else " (bogus!)"
        print(f"Dates for file: {name}{shown}")
        if not astat:
            return 2
        stamp = astat.st_mtime
        there = sdate.dttm_from_ux_stamp(stamp)
        dump_dates(there)
        print("")
    return 0


def dump_dates(now):
    shown = sdate.date_to_string(now)
    print(f"date_to_string() = {shown}")
    shown = sdate.datetime_to_string(now)
    print(f"datetime_to_string() = {shown}")
    dtx = sdate.Datex("2022-01-16")
    print(dtx, "; epoch_day():", dtx.epoch_day())
    greg = dtx.ordinal()
    assert sdate.Datex("1971-01-01").epoch_day() == 0
    back = sdate.Datex()
    back.from_ordinal(greg)
    assert str(back) == "2022-01-16"
    assert back.epoch_day() == dtx.epoch_day()


#
# Test suite
#
if __name__ == "__main__":
    main()
