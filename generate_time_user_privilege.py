# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime, timedelta

from database_util import session_scope

BASE_DATE = datetime(2015, 10, 1)


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


def previous_day(time):
    return time - timedelta(days=1)


def new_padded_list(length, fill_value):
    return [fill_value] * length


def generate_user_trace(user_id):
    with session_scope() as db:
        rows = db.execute('select wifi_user_action_log_id, '
                            '       beneficiary_user_id, '
                            '       case credit_definition_id when 0 then 2 when 1 then 1 end as privilege_level, '
                            '       duration, '
                            '       log_time '
                            'from wifi_user_action_logs '
                            'where beneficiary_user_id = :user_id '
                            'and duration >= 120 '
                            'order by wifi_user_action_log_id asc',
                          {'user_id': user_id})
        if rows.rowcount == 0:
            return None

        trace_list = [0]
        new_privilege_deadline = dict()
        new_privilege_deadline[1] = BASE_DATE
        new_privilege_deadline[2] = BASE_DATE

        now = datetime.now()
        for row in rows:
            log_time = row['log_time']
            privilege_level = row['privilege_level']
            duration = row['duration']
            mark_free_start_date = None

            # resetting deadlines
            if new_privilege_deadline[1] <= log_time and new_privilege_deadline[2] <= log_time:
                max_last_deadline = max(new_privilege_deadline[1], new_privilege_deadline[2])
                new_privilege_deadline[1] = new_privilege_deadline[2] = log_time
                # marking start date of "free using time"
                mark_free_start_date = next_day(max_last_deadline)
            elif new_privilege_deadline[2] < new_privilege_deadline[1]:
                new_privilege_deadline[2] = log_time

            old_privilege_deadline = deepcopy(new_privilege_deadline)

            delta_duration = timedelta(minutes=duration)
            if privilege_level == 2:
                new_privilege_deadline[2] += delta_duration
                new_privilege_deadline[1] += delta_duration
            elif privilege_level == 1:
                new_privilege_deadline[1] += delta_duration

            # marking in array
            # 1. marking free time if possible
            if mark_free_start_date is not None:
                extended_list = new_padded_list(
                    date_difference(log_time, mark_free_start_date) + 1,
                    0)
                trace_list.extend(extended_list)

            # 2. marking action logs
            if privilege_level == 2:
                trace_list[-1] = 2
                if old_privilege_deadline[2] < old_privilege_deadline[1]:
                    extended_list = new_padded_list(
                        date_difference(new_privilege_deadline[1], old_privilege_deadline[1]),
                        1)
                    trace_list.extend(extended_list)

                    replace_start_index = date_difference(old_privilege_deadline[2])
                    replace_end_index = date_difference(new_privilege_deadline[2])

                    for i in range(replace_start_index, replace_end_index + 1, 1):
                        trace_list[i] = 2
                else:
                    extended_list = new_padded_list(
                        date_difference(new_privilege_deadline[2], old_privilege_deadline[2]),
                        2)
                    trace_list.extend(extended_list)
            if privilege_level == 1:
                trace_list[-1] = 1
                extended_list = new_padded_list(
                    date_difference(new_privilege_deadline[1], old_privilege_deadline[1]),
                    1)
                trace_list.extend(extended_list)
        return trace_list

print "==============="
#generate_user_trace(86868)
trace = generate_user_trace(9)
print trace

a = datetime(2016, 7, 1)
b = datetime(2016, 7, 1, 23, 59, 59)

print date_difference(a, b)

