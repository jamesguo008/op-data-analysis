# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from sqlalchemy.sql import text

from database_util import session_scope
from toolkit import date_range, BASE_DATE, MAX_DATE


class UserUsage:
    user_id = None
    account_name = None
    factory_sequence_id = None
    factory_name = None
    time = None

    def __to_string(self):
        return '< user_id: ' + self.user_id.__str__() \
               + ', account_name: ' + self.account_name \
               + ', factory_sequence_id: ' + self.factory_sequence_id \
               + ', factory_name: ' + self.factory_name \
               + ', time: ' + self.time.__str__() + ' >'

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()


factory_sql = text('select user_id, account_name, factory_sequence_id, name from user_factory_from_last_non_public ')
relation_sql = text('select distinct mac, user_id '
                    'from mac_user_daily_relations '
                    'where start_time <= date_add(:date, INTERVAL 1 DAY) '
                    'and end_time >= cast(:date as datetime) ')
stats_sql = text('select mac from wifi_auth_online_stats where file_date = date_format(:date, \'%Y%m%d\')')

insert_sql = text('insert into time_user_usages(user_id, time) values (:user_id, :time) ')


def generate_user_factory_dict():
    with session_scope() as db:
        user_factory_relations = dict()

        factory_rows = db.execute(factory_sql)

        for row in factory_rows:
            user_factory_relation = UserUsage()
            user_id = row['user_id']
            user_factory_relation.user_id = user_id
            user_factory_relation.account_name = row['account_name']
            user_factory_relation.factory_name = row['name']
            user_factory_relation.factory_sequence_id = row['factory_sequence_id']
            user_factory_relations[user_id] = user_factory_relation

    return user_factory_relations


def generate_mac_user_relations(time):
    with session_scope() as db:
        mac_user_root = dict()

        relation_rows = db.execute(relation_sql, {'date': time})
        for row in relation_rows:
            mac = row['mac']
            user_id = row['user_id']

            mac_list = mac_user_root.get(mac)
            if mac_list is None:
                mac_list = list()
                mac_user_root[mac] = mac_list

            mac_list.append(user_id)

    return mac_user_root


def get_wifi_auth_online_macs(time):
    with session_scope() as db:
        macs = list()

        mac_rows = db.execute(stats_sql, {'date': time})

        for row in mac_rows:
            macs.append(row['mac'])

    print("macs on ", time, ": ", macs.__len__())
    return macs


def generate_uv_user_time(time, factory_dict=None):

    print("processing: ", time)
    if factory_dict is None:
        factory_dict = generate_user_factory_dict()

    mac_user_relations = generate_mac_user_relations(time)
    online_macs = get_wifi_auth_online_macs(time)

    online_user_id_set = set()
    online_user_info_set = set()
    empty_mac = set()
    for mac in online_macs:
        user_id_list = mac_user_relations.get(mac)

        if user_id_list is None:
            empty_mac.add(mac)
            continue

        for user_id in user_id_list:
            online_user_id_set.add(user_id)

    with session_scope() as db:
        for user_id in online_user_id_set:
            db.execute(insert_sql, {'user_id': user_id, 'time': time})

    print("finish processing: ", time, ", length: ", online_user_id_set.__len__())


start_time = datetime.now()

user_factory_dict = generate_user_factory_dict()
with ThreadPoolExecutor(max_workers=8) as executor:
    for time in date_range(BASE_DATE, MAX_DATE):
        executor.submit(generate_uv_user_time, time, user_factory_dict)
end_time = datetime.now()

print('total time elapsed: ', end_time - start_time)
