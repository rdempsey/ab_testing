#!/usr/bin/env python

from datetime import datetime

_epoch = datetime(1970, 1, 1)


def iso_time_format(datetime_):
    """
    Format a datetime in ISO format.

    :param datetime_: datetime to format.
    :return: datetime formatted as 2019-02-03T10:53:18.322Z
    """
    return '%04d-%02d-%02dT%02d:%02d:%02d.%03dZ' % (
        datetime_.year, datetime_.month, datetime_.day, datetime_.hour, datetime_.minute, datetime_.second,
        int(datetime_.microsecond / 1000))


def epoch_nano_second(datetime_):
    """
    Get the nano seconds of a datetime since the epoch.

    :param datetime_: datetime to use for calculation.
    :return: date formatted as 1549191198322771000
    """
    return int((datetime_ - _epoch).total_seconds()) * 1000000000 + datetime_.microsecond * 1000
