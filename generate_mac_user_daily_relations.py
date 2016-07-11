# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from sys import exc_info

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from database_util import session_scope
from toolkit import get_max_user_id, ifnull

session_sql = text('select * from user_sessions '
                   'where user_id = :user_id '
                   'and created_at >= \'2015-07-01\' '
                   'order by user_session_id asc')

insert_sql = text('insert into mac_user_daily_relations (mac, user_id, start_time, end_time)'
                  'values (:mac, :user_id, :start_time, :end_time)')

invalid_macs = {'null': 1, '00:00:00:00:00:00': 1, ':::::': 1, '': 1}


class MacUserDailyRelation:
    mac_user_daily_relation_id = None
    mac = ''
    user_id = None
    start_time = None
    end_time = None

    def __init__(self, user_session):
        self.mac = user_session['mac']
        self.user_id = user_session['user_id']
        self.start_time = user_session['created_at']
        self.end_time = ifnull(user_session['revoked_at'], user_session['expired_at'])

    def __str__(self):
        return self.__to_string()

    def __repr__(self):
        return self.__to_string()

    def __to_string(self):
        return '< user_id: ' + self.user_id.__str__() \
               + ', mac: ' + self.mac \
               + ', start_time: ' + self.start_time.__str__() \
               + ', end_time: ' + self.end_time.__str__() + ' >'


def generate_user_session_trace(user_id):
    records = list()
    with session_scope() as db:
        rows = db.execute(session_sql, {'user_id': user_id})
        if rows.rowcount == 0:
            return None

        print('processing ', user_id)
        record = None
        old_mac = ''
        for row in rows:
            created_at = row['created_at']
            expired_at = row['expired_at']
            revoked_at = row['revoked_at']
            status = row['status']
            mac = row['mac']
            if invalid_macs.get(mac) is not None:
                mac = old_mac
            else:
                old_mac = mac

            is_need_push = False

            if record is None:
                record = MacUserDailyRelation(row)
                record.mac = mac
            elif record.mac != mac:
                record.end_time = created_at
                records.append(record)
                record = MacUserDailyRelation(row)
                record.mac = mac
            else:
                if status == 6:
                    record.end_time = ifnull(revoked_at, expired_at)
                elif status == 5:
                    record.end_time = expired_at
                    is_need_push = True
                elif status == 4:
                    record.end_time = revoked_at
                    is_need_push = True
                elif status == 3 or status == 2:
                    record.end_time = revoked_at
                    is_need_push = True
                else:
                    pass

            if is_need_push:
                records.append(record)
                record = None

        if record is not None:
            records.append(record)
        for record in records:
            try:
                db.execute(insert_sql,
                           {'mac': record.mac,
                                'user_id': user_id,
                                'start_time': record.start_time,
                                'end_time': record.end_time})
            except IntegrityError as ie:
                etype, val, tb = exc_info()
                #traceback.print_exception(etype, val, tb)
                pass

    print('finish processing ', user_id)


max_user_id = get_max_user_id()
start_time = datetime.now()
with ThreadPoolExecutor(max_workers=16) as executor:
    for i in range(1, max_user_id + 1, 1):
#        generate_user_session_trace(i)
        executor.submit(generate_user_session_trace, i)
end_time = datetime.now()

print('total time eclapsed: ', end_time - start_time)



