# -*- coding: utf-8 -*-
# gw_change_points need to import every day

from database_util import session_scope
from sqlalchemy.sql import text

with session_scope() as conn:
    gw_ids = conn.execute('select gw_id from gw_change_points group by gw_id having count(1)>1;')
    for gw_id in gw_ids:
        sql = text("select * from gw_change_points where gw_id = :gw order by start_time desc")
        sql = sql.bindparams(gw=gw_id[0])
        rows = conn.execute(sql)
        first_itor = True
        for row in rows:
            if (first_itor):
                first_itor = False
                change_date = row["start_time"]
                continue
            sql = text("update gw_change_points set next_use_time=:nut where gw_change_point_id=:id")
            sql = sql.bindparams(nut=change_date, id=row["gw_change_point_id"])
            conn.execute(sql)
            change_date = row["start_time"]