# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from database_util import session_scope

BASE_DATE = datetime(2015, 10, 1)
MAX_DATE = datetime(2016, 7, 5)


def get_max_user_id():
    with session_scope() as db:
        result = db.execute('select max(beneficiary_user_id) as max_user_id from wifi_user_action_logs')

        for row in result:
            max_user_id = row['max_user_id']

    return max_user_id


def datetime_difference(later, earlier=BASE_DATE):
    delta = later - earlier
    return delta.days


def date_difference(later, earlier=BASE_DATE):
    delta = later.date() - earlier.date()
    return delta.days


def next_day(time):
    return time + timedelta(days=1)


def add_day(n, time):
    return time + timedelta(days=n)


def previous_day(time):
    return time - timedelta(days=1)


def new_padded_list(length, fill_value):
    return [fill_value] * length


def add_day(n, base_date=BASE_DATE):
    return base_date + timedelta(days=n)


def format_date(time):
    return time.strftime("%Y-%m-%d")


def ifnull(var, val):
    if var is None:
        return val
    return var