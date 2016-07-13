# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from sqlalchemy.sql import text

from database_util import session_scope
from toolkit import date_range, MAX_DATE

select_sql = text('select distinct f.user_id, f.account_name, f.factory_sequence_id, f.name, :date from ('
                  '(select mac from wifi_auth_online_stats where file_date = date_format(:date, \'%Y%m%d\')) waos '
                  'join '
                  '(select distinct mac, user_id from mac_user_daily_relations '
                  'where start_time <= date_add(:date, INTERVAL 1 DAY) '
                  'and end_time >= cast(:date as datetime)) mudr '
                  'on mudr.mac = waos.mac '
                  'join '
                  '(select * from user_factory_from_last_non_public) f '
                  'on f.user_id = mudr.user_id)')


def generate_uv_user_time(time):
    print("time: ", time)
    with session_scope() as db:
        rows = db.execute(select_sql, {'date': time})

        for row in rows:
            print(row)

        print("rowcount: ", rows.rowcount)

start_time = datetime.now()
with ThreadPoolExecutor(max_workers=4) as executor:
    for date in date_range(datetime(2016, 7, 1), MAX_DATE):
#        generate_uv_user_time(date)
        executor.submit(generate_uv_user_time, date)
end_time = datetime.now()

print('total time elapsed: ', end_time - start_time)

