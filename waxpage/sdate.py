# sdate.py  (c)2020  Henrique Moreira

""" sdate - Easy hard-coded functions to convert dates

  Compatibility: python 3.
"""

# pylint: disable=missing-function-docstring


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


class Datex():
    """ Keeps Gregorian date in the object.
    You can easily use Linux epoch_day() here.
    """
    _invalid = datetime.date(1971, 1, 1)
    _invalid_str = "-"

    def __init__(self, obj=None):
        if obj is None:
            self._date = Datex._invalid
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            self._set_from_dttm(obj)
        else:
            self._set_from_data(obj)
        self._greg_ord = self._date.toordinal()

    def _set_from_dttm(self, obj):
        self._date = datetime.date(obj.year, obj.month, obj.day)

    def _set_from_data(self, adate):
        try:
            dttm = datetime.datetime.strptime(adate, "%Y-%m-%d")
        except ValueError:
            dttm = datetime.datetime.strptime(adate, "%Y-%m-%d %H:%M")
        self._date = dttm

    def __str__(self) -> str:
        if self.epoch_day() <= 0:
            return Datex._invalid_str
        return self._date.strftime("%Y-%m-%d")

    def ordinal(self) -> int:
        assert self._greg_ord >= 0
        return self._greg_ord

    def from_ordinal(self, greg_ord:int):
        assert greg_ord >= 0
        self._date = datetime.datetime.fromordinal(greg_ord)
        self._greg_ord = greg_ord

    def epoch_day(self) -> int:
        delta = self._greg_ord - datetime.date(1971, 1, 1).toordinal()
        assert delta >= 0
        return delta


#
# Test suite
#
if __name__ == "__main__":
    print("Import, or see tests at sdate.test.py")
