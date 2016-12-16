# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta

import xlrd
from xlrd import open_workbook
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 常量初始化
WEEK_CHINESE = ('一', '二', '三', '四', '五', '六', '日')
WEEKEND = ('六', '日')
START_DATE = datetime(2016, 12, 1, 6, 0, 0, 0)
PRE_DAY = (2016, 12, 1, 6, 0, 0)
LATE_HOUR_LINE = 10
OFF_HOUR_LINE = 18
OFF_MINUTE_LINE = 30
DEPART_H = 6
OUTPUT_DIR = '/home/jamesguo/tongji_test/'
OUTPUT_FILE_NAME = OUTPUT_DIR + 'result.xlsx'
INPUT_FILE_NAME = OUTPUT_DIR + 'daka.xls'


def datetime_judge(v_datetime):
    if v_datetime[3] < DEPART_H:
        key_date = str(v_datetime[1]).zfill(2) + str(v_datetime[2] - 1).zfill(2)
    else:
        key_date = str(v_datetime[1]).zfill(2) + str(v_datetime[2]).zfill(2)
    return key_date


wb = open_workbook(INPUT_FILE_NAME)
sh = wb.sheet_by_index(0)
# 读取、组织数据
organize_dict = {}
for row in range(1, sh.nrows, 1):
    name = sh.cell(row, 1).value
    num = sh.cell(row, 2).value
    fingerprint_time = xlrd.xldate_as_tuple(sh.cell(row, 3).value, wb.datemode)

    key_date = datetime_judge(fingerprint_time)
    if name in organize_dict:
        if key_date in organize_dict[name]:
            organize_dict[name][key_date].append(fingerprint_time)
        else:
            organize_dict[name][key_date] = [fingerprint_time]
    else:
        organize_dict[name] = {key_date: [fingerprint_time]}

# 创建表格
book = xlsxwriter.Workbook(OUTPUT_FILE_NAME)
full_sheet = book.add_worksheet('汇总')
ot_sheet = book.add_worksheet('加班情况判断')
print_stat_sheet = book.add_worksheet('上班情况判断')
print_time_sheet = book.add_worksheet('打卡时间')
# 准备cell格式
border_on = book.add_format({'border': 1})
cell_format_all_center = book.add_format({'align': 'center', 'valign': 'vcenter'})
cell_format_left_center = book.add_format({'align': 'left', 'valign': 'vcenter'})
cell_format_left_center_wrap = book.add_format({'align': 'left', 'valign': 'vcenter', 'text_wrap': 'on'})
cell_format_not_normal = book.add_format({'bg_color': 'yellow', 'align': 'center', 'valign': 'vcenter'})
cell_format_miss_print = book.add_format({'bg_color': 'gray', 'align': 'center', 'valign': 'vcenter'})
# 加黑边
full_sheet.conditional_format(0, 0, 1000, 1000, {'type': 'no_errors', 'format': border_on})
ot_sheet.conditional_format(0, 0, 1000, 1000, {'type': 'no_errors', 'format': border_on})
print_stat_sheet.conditional_format(0, 0, 1000, 1000, {'type': 'no_errors', 'format': border_on})
print_time_sheet.conditional_format(0, 0, 1000, 1000, {'type': 'no_errors', 'format': border_on})
# 画表格头，日期与星期
full_sheet.write(0, 0, '日期', cell_format_all_center)
ot_sheet.write(0, 0, '日期', cell_format_all_center)
print_stat_sheet.write(0, 0, '日期', cell_format_all_center)
print_time_sheet.write(0, 0, '日期', cell_format_all_center)
full_sheet.write(1, 0, '星期', cell_format_all_center)
ot_sheet.write(1, 0, '星期', cell_format_all_center)
print_stat_sheet.write(1, 0, '星期', cell_format_all_center)
print_time_sheet.write(1, 0, '星期', cell_format_all_center)
tmp_datetime = START_DATE
old_month = tmp_datetime.month
date_col_dict = dict()
col = 1
except_weekend_date = []
while old_month == tmp_datetime.month:
    v_key = str(tmp_datetime.month).zfill(2) + str(tmp_datetime.day).zfill(2)
    v_day = str(tmp_datetime.day)
    v_week = WEEK_CHINESE[tmp_datetime.weekday()]
    full_sheet.write(0, col, v_day, cell_format_all_center)
    ot_sheet.write(0, col, v_day, cell_format_all_center)
    print_stat_sheet.write(0, col, v_day, cell_format_all_center)
    print_time_sheet.write(0, col, v_day, cell_format_all_center)
    full_sheet.write(1, col, v_week, cell_format_all_center)
    ot_sheet.write(1, col, v_week, cell_format_all_center)
    print_stat_sheet.write(1, col, v_week, cell_format_all_center)
    print_time_sheet.write(1, col, v_week, cell_format_all_center)
    date_col_dict[v_key] = col
    if v_week in WEEKEND:
        except_weekend_date.append(v_key)
    col += 1
    tmp_datetime += timedelta(days=1)

# 输出结果
row = 2
for (name, fpt) in sorted(organize_dict.items()):
    full_sheet.write(row, 0, name, cell_format_all_center)
    ot_sheet.write(row, 0, name, cell_format_all_center)
    print_stat_sheet.write(row, 0, name, cell_format_all_center)
    print_time_sheet.write(row, 0, name, cell_format_all_center)
    max_line = 1
    for date in sorted(date_col_dict.keys()):
        # 无打卡记录，设置为漏打卡，排除周末
        if date not in organize_dict[name]:
            if date not in except_weekend_date:
                full_sheet.write(row, date_col_dict[date], '漏打卡', cell_format_miss_print)
                print_stat_sheet.write(row, date_col_dict[date], '漏打卡', cell_format_miss_print)
                continue
            else:
                continue
        # 输出打卡时间，并在其他表格以标注形式展现
        print_time_list = sorted(organize_dict[name][date])
        if len(print_time_list) > max_line:
            max_line = len(print_time_list)
        print_time_str = ""
        for iter_time in print_time_list:
            print_time_str += str(iter_time[2]).zfill(2) + '日'
            print_time_str += str(iter_time[3]).zfill(2) + ':' + str(iter_time[4]).zfill(2) + ':' + str(iter_time[5]).zfill(2) + '\r\n'
        print_time_sheet.write(row, date_col_dict[date], print_time_str[0:-1], cell_format_left_center_wrap)
        full_sheet.write_comment(row, date_col_dict[date], print_time_str[0:-1])
        ot_sheet.write_comment(row, date_col_dict[date], print_time_str[0:-1])
        print_stat_sheet.write_comment(row, date_col_dict[date], print_time_str[0:-1])
        # 判断上下班情况
        if len(print_time_list) == 1:
            full_sheet.write(row, date_col_dict[date], '漏打卡', cell_format_miss_print)
            print_stat_sheet.write(row, date_col_dict[date], '漏打卡', cell_format_miss_print)
            continue
        min_date = datetime(print_time_list[0][0], print_time_list[0][1], print_time_list[0][2], print_time_list[0][3], print_time_list[0][4], print_time_list[0][5])
        max_date = datetime(print_time_list[-1][0], print_time_list[-1][1], print_time_list[-1][2], print_time_list[-1][3], print_time_list[-1][4], print_time_list[-1][5])
        print_status = ""
        if min_date.hour >= LATE_HOUR_LINE:
            print_status += '迟到,'
        if (max_date.hour < OFF_HOUR_LINE) or (max_date.hour == OFF_HOUR_LINE and max_date.minute < OFF_MINUTE_LINE):
            print_status += '早退,'
        if len(print_status) != 0:
            full_sheet.write(row, date_col_dict[date], print_status[0:-1], cell_format_not_normal)
            print_stat_sheet.write(row, date_col_dict[date], print_status[0:-1], cell_format_not_normal)
        # 加班情况
        if len(print_status) == 0:
            if max_date.hour == 20:
                full_sheet.write(row, date_col_dict[date], 15, cell_format_all_center)
                ot_sheet.write(row, date_col_dict[date], 15, cell_format_all_center)
            elif max_date.hour >= 21 or max_date.day > min_date.day:
                full_sheet.write(row, date_col_dict[date], 65, cell_format_all_center)
                ot_sheet.write(row, date_col_dict[date], 65, cell_format_all_center)
    # 调整高度，容易显示
    print_time_sheet.set_row(row, 15 * max_line)
    full_sheet.write_formula(row, col, '{=SUM(%s:%s)}' % (xl_rowcol_to_cell(row, 0), xl_rowcol_to_cell(row, col - 1)))
    ot_sheet.write_formula(row, col, '{=SUM(%s:%s)}' % (xl_rowcol_to_cell(row, 0), xl_rowcol_to_cell(row, col - 1)))
    row += 1
# 设置单元格宽度
full_sheet.set_column(1, col - 1, 8)
ot_sheet.set_column(1, col - 1, 4)
print_stat_sheet.set_column(1, col - 1, 8)
print_time_sheet.set_column(1, col - 1, 12)
# 固定表头，容易观察
full_sheet.freeze_panes(2, 1)
ot_sheet.freeze_panes(2, 1)
print_stat_sheet.freeze_panes(2, 1)
print_time_sheet.freeze_panes(2, 1)
# 保存收工
book.close()
