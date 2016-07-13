# -*- coding: utf-8 -*-

from database_util import session_scope

with session_scope() as db:
    print("getting uv_rows")
    uv_rows = db.execute('select mac from wifi_auth_online_stats where file_date = 20160704')

    uv_macs = dict()

    print("processing uv_rows")
    for uv_row in uv_rows:
        uv_macs[uv_row['mac']] = 1

    print("getting used_rows")
    used_rows = db.execute("select mudr.mac "
                           "from wifi_auth_online_stats waos, "
                           "mac_user_daily_relations mudr "
                           "where waos.file_date = '20160704' "
                           "and waos.mac = mudr.mac "
                           "and mudr.start_time <= '2016-07-04' "
                           "and mudr.end_time >= '2016-07-04'")

    print("processing used_rows")
    used_macs = dict()
    for used_row in used_rows:
        mac = used_row['mac']
        used_macs[mac] = 1

diff_macs = dict()
for key, value in uv_macs.items():
    if used_macs.get(mac) is None:
        diff_macs[mac] = 1

print("results:")
for key, value in diff_macs.items():
    print(key)
