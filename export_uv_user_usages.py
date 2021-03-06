# -*- coding: utf-8 -*-

from datetime import datetime

import xlsxwriter
from sqlalchemy.sql import text

from database_util import session_scope
from toolkit import get_max_user_id, date_difference, add_day, format_date, BASE_DATE, MAX_DATE


start = datetime.now()

output_dir = r'/home/maxwong/data-analysis/'
file_name = 'user_usages.xlsx'

file = output_dir + file_name

book = xlsxwriter.Workbook(file)
sheet = book.add_worksheet('user_usage')

cell_format_all_center = book.add_format({'align': 'center', 'valign': 'vcenter'})

sheet.write(0, 1, '工厂', cell_format_all_center)

date_col_dict = dict()

max_col = 0


for i in range(0, date_difference(MAX_DATE, BASE_DATE), 1):
    time = add_day(i, BASE_DATE)
    max_col = col = i + 2
    sheet.write(0, col, format_date(time), cell_format_all_center)
    date_col_dict[time] = col

sheet.set_column(1, 1, 18)
sheet.set_column(2, max_col, 10)

max_user_id = get_max_user_id()
usage_sql = text('select * from time_user_usages where user_id = :user_id')
factory_sql = text('select * from user_factory_from_last_non_public where user_id = :user_id')

cur_row = 0
cur_col = 0

FACTORY_PUBLIC = 'PUBLIC(PUBLIC)'

with session_scope() as db:
    for user_id in range(1, max_user_id + 1, 1):
        usage_rows = db.execute(usage_sql, {'user_id': user_id})

        if usage_rows.rowcount == 0:
            continue

        print("processing user_id: ", user_id)
        cur_row += 1
        cur_col = 0
        factory_rows = db.execute(factory_sql, {'user_id': user_id})

        if factory_rows.rowcount == 0:
            factory = FACTORY_PUBLIC
        else:
            for row in factory_rows:
                factory_sequence_id = row['factory_sequence_id']
                factory_name = row['name']
                if factory_sequence_id == '':
                    factory = FACTORY_PUBLIC
                else:
                    factory = factory_name + '(' + factory_sequence_id + ')'
        sheet.write(cur_row, cur_col, user_id)
        cur_col += 1
        sheet.write(cur_row, cur_col, factory)
        cur_col += 1

        for row in usage_rows:
            time = row['time']
            if row['time'] >= MAX_DATE:
                continue

            sheet.write(cur_row, date_col_dict[time], 1)
        print("finish processing user_id: ", user_id)


book.close()
end = datetime.now()

print("total time used: ", end - start)

