# -*- coding: utf-8 -*-

import traceback
from contextlib import contextmanager
from sys import exc_info

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_engine = create_engine('mysql+pymysql://op_data_analysis:op_data_analysis@sdcm210:3406/op_data_analysis?charset=utf8',
                          encoding='utf-8',
                          echo=False,
                          pool_size=4)
db_session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)


@contextmanager
def session_scope():
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        etype, val, tb = exc_info()
        traceback.print_exception(etype, val, tb)
        session.rollback()
    finally:
        session.close()

