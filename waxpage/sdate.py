# sdate.py  (c)2020  Henrique Moreira

"""
  sdate - Easy hard-coded functions to convert dates

  Compatibility: python 3.
"""
# pylint: disable=unused-argument

import datetime

def current():
    """ Returns the current dttm struct """
    return datetime.datetime.now()

def from_abbrev_date(date_string) -> datetime.datetime:
    """ Converts string to datetime object. """
    return datetime.datetime.strptime(date_string, "%d.%m.%Y")

def date_to_string(dttm, sep=".") -> str:
    """ Returns the date string from dttm struct """
    return dttm.strftime(f"%d{sep}%m{sep}%Y")

def datetime_to_string(dttm, sep=".") -> str:
    """ Returns the date and time string from dttm struct """
    return dttm.strftime(f"%d{sep}%m{sep}%Y %H:%M:%S")

def dttm_from_ux_stamp(stamp):
    """ Returns dttm struct from Unix timestamp.
        i.e. epoch.
        Epoch 0 is: datetime(1970, 1, 1, 1, 0)
    """
    # epoch = datetime.datetime.fromtimestamp(0) =
    #	... epoch.__str__() = '1970-01-01 01:00:00'
    assert isinstance(stamp, (int, float))
    return datetime.datetime.fromtimestamp(stamp)


#
# Test suite
#
if __name__ == "__main__":
    print("Import, or see tests at sdate.test.py")
