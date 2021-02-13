# uxdate.py  (c)2021  Henrique Moreira

"""
uxdate - Unix Dates helpers and wrappers.
"""

# pylint: disable=unused-argument

import os
import datetime
import time
from time import strptime

def date_from_cvs_entry_str(astr):
    """ Converts date within one line of a CVS 'Entries' text file,
    E.g.
		/fname/1.2/Sat Feb 13 21:29:59 2021//
    """
    fmt = "%a %b %d %H:%M:%S %Y"
    if isinstance(astr, time.struct_time):
        mytime = astr
        new = time.strftime(fmt, mytime)
        assert isinstance(new, str)
        return date_from_cvs_entry_str(new)
    assert isinstance(astr, str)
    mytime = strptime(astr, fmt)
    timestamp = time.mktime(mytime)
    dttm = datetime.datetime.fromtimestamp(timestamp)
    #dttm = datetime.date.fromtimestamp(timestamp)
    return dttm

def date_from_cvs_v_format(astr):
    """ Returns the datetime date for CVS 'astr' date,
    Example:	2021.02.13.18.43.59; stands for 13-Feb.2021, at around 18:43!
    """
    fmt = "%Y.%m.%d.%H.%M.%S"
    timestamp = time.mktime(strptime(astr, fmt))
    return datetime.datetime.fromtimestamp(timestamp)

def same_second(dttm1, dttm2) -> bool:
    """ Checks whether timestamps or dates match to the second granularity """
    if isinstance(dttm1, (float, int)):
        return int(dttm1) == int(dttm2)
    same = dttm1.year == dttm2.year and \
           dttm1.month == dttm2.month and \
           dttm1.day == dttm2.day and \
           dttm1.hour == dttm2.hour and \
           dttm1.minute == dttm2.minute and \
           dttm1.second == dttm2.second
    return same

def basic_date(adate) -> str:
    """ Returns a basic date string, basic Year-To-day format.
    """
    assert adate is not None
    assert not isinstance(adate, str)
    fmt = "%Y-%m-%d %H:%M:%S"
    if isinstance(adate, (float, int)):
        timestamp = adate
        dttm = datetime.datetime.fromtimestamp(timestamp)
    else:
        dttm = adate
    astr = dttm.strftime(fmt)
    return astr


def posix_touch(path, dttm) -> bool:
    """ Touches file/ dir at 'path' """
    stamp = datetime.datetime.timestamp(dttm)
    u_time = (stamp, stamp)
    os.utime(path, u_time)
    return True
