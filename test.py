# -*- coding: utf-8 -*-

from database_util import session_scope

with session_scope() as conn:
    conn.execute('update time_user_privileges set user_id = 5 where user_id = 3')
    rows = conn.execute('select * from time_user_privileges')
    for row in rows:
        print row