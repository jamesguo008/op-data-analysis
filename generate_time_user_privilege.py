# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta

from sqlalchemy.sql import text

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


def add_day(n, base_date=BASE_DATE):
    return base_date + timedelta(days=n)


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
        new_privilege_deadlines = dict()
        new_privilege_deadlines[1] = BASE_DATE
        new_privilege_deadlines[2] = BASE_DATE

        now = datetime.now()
        for row in rows:
            log_time = row['log_time']
            privilege_level = row['privilege_level']
            duration = row['duration']
            mark_free_start_date = None
            max_wifi_user_action_log_id = row['wifi_user_action_log_id']

            # resetting deadlines
            if new_privilege_deadlines[1] <= log_time and new_privilege_deadlines[2] <= log_time:
                max_last_deadline = max(new_privilege_deadlines[1], new_privilege_deadlines[2])
                new_privilege_deadlines[1] = new_privilege_deadlines[2] = log_time
                # marking start date of "free using time"
                mark_free_start_date = next_day(max_last_deadline)
            elif new_privilege_deadlines[1] < log_time:
                new_privilege_deadlines[1] = log_time
            elif new_privilege_deadlines[2] < log_time:
                new_privilege_deadlines[2] = log_time

            old_privilege_deadlines = deepcopy(new_privilege_deadlines)

            delta_duration = timedelta(minutes=duration)
            if privilege_level == 2:
                new_privilege_deadlines[2] += delta_duration
                new_privilege_deadlines[1] += delta_duration
            elif privilege_level == 1:
                new_privilege_deadlines[1] += delta_duration

            # marking in array
            # 1. marking free time if possible
            if mark_free_start_date is not None:
                extended_list = new_padded_list(
                    date_difference(log_time, mark_free_start_date) + 1,
                    0)
                trace_list.extend(extended_list)

            # 2. marking action logs

            pay_day = date_difference(log_time)
            # paid user
            if privilege_level == 2:
                # mark the pay day
                trace_list[pay_day] = 2

                if old_privilege_deadlines[2] < old_privilege_deadlines[1]:
                    extended_list = new_padded_list(
                        date_difference(new_privilege_deadlines[1], old_privilege_deadlines[1]),
                        1)
                    trace_list.extend(extended_list)

                    replace_start_index = date_difference(old_privilege_deadlines[2])
                    replace_end_index = date_difference(new_privilege_deadlines[2])

                    for i in range(replace_start_index, replace_end_index + 1, 1):
                        trace_list[i] = 2
                else:
                    extended_list = new_padded_list(
                        date_difference(new_privilege_deadlines[2], old_privilege_deadlines[2]),
                        2)
                    trace_list.extend(extended_list)
            elif privilege_level == 1:
                if trace_list[pay_day] < 1:
                    trace_list[pay_day] = 1
                extended_list = new_padded_list(
                    date_difference(new_privilege_deadlines[1], old_privilege_deadlines[1]),
                    1)
                trace_list.extend(extended_list)
        result = dict()

        result['trace_list'] = trace_list
        result['user_id'] = user_id
        result['privilege_deadlines'] = new_privilege_deadlines
        result['max_wifi_user_action_log_id'] = max_wifi_user_action_log_id
        return result


def log_time_user_privileges(trace_result):
    with session_scope() as db:
        user_id = trace_result['user_id']
        trace_list = trace_result['trace_list']

        stmt = text('insert into time_user_privileges (time, user_id, privilege_level) '
                    'values (:time, :user_id, :privilege_level)')
        for offset, privilege_level in enumerate(trace_list):
            if privilege_level == 0:
                continue
            time = add_day(offset)
            db.execute(stmt, {'time': time, 'user_id': user_id, 'privilege_level': privilege_level})


def log_user_latest_deadlines(trace_result):
    user_id = trace_result['user_id']
    wifi_user_action_log_id = trace_result['max_wifi_user_action_log_id']
    privilege_deadlines = trace_result['privilege_deadlines']
    stmt = text('insert into user_latest_deadlines (user_id, wifi_user_action_log_id, privilege_level, deadline) '
                'values (:user_id, :wifi_user_action_log_id, :privilege_level, :deadline)')
    with session_scope() as db:
        for privilege_level, privilege_deadline in privilege_deadlines.items():
            db.execute(stmt,
                       {
                           'user_id': user_id,
                           'wifi_user_action_log_id': wifi_user_action_log_id,
                           'privilege_level': privilege_level,
                           'deadline': privilege_deadline
                       })


def analyse_user_usage(user_id):
    trace_result = generate_user_trace(user_id)
    if trace_result is not None:
        print("processing user_id: ", user_id)
        log_time_user_privileges(trace_result)
        log_user_latest_deadlines(trace_result)
        print("finish processing user_id: ", user_id)


print("===============")
#generate_user_trace(12345)

max_user_id = get_max_user_id()
print("max_user_id: ", max_user_id)

start = datetime.now()
print("calculation started at ", start)
with ThreadPoolExecutor(max_workers=8) as executor:
    for user_id in range(1, max_user_id + 1, 1):
#        analyse_user_usage(user_id)
        executor.submit(analyse_user_usage, user_id)


end = datetime.now()
print("calculation ended at ", end)
print(end - start)
