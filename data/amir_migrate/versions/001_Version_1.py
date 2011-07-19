#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2010 <jooyeshgar> <info@jooyeshgar.com>
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy import *
from migrate import *
import logging

meta = MetaData()

#New tables (version 1):
subject = Table('subject', meta,
    Column('id', Integer, primary_key=True),
    Column('code', String(20), nullable=False),
    Column('name', Unicode(60), nullable=False),
    Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id'), nullable=False),
    Column('lft', Integer, nullable=False),
    Column('rgt', Integer, nullable=False),
    Column('type', Integer)
)

bill = Table('bill', meta,
    Column('id', Integer, primary_key=True),
    Column('number', Integer, nullable = False),
    Column('creation_date', Date, nullable = False),
    Column('lastedit_date', Date, nullable = False),
    Column('date', Date, nullable = False),
    Column('permanent', Boolean, ColumnDefault(False), nullable = False)
)

notebook = Table('notebook', meta,
    Column('id', Integer, primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id')),
    Column('bill_id', Integer, ForeignKey('bill.id')),
    Column('desc', Unicode, ColumnDefault("")),
    Column('value', Integer, ColumnDefault(0), nullable = False)
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    
    subject.create(checkfirst=True)
    bill.create(checkfirst=True)
    notebook.create(checkfirst=True)

    #Insert test data
    op = subject.insert()
    op.execute({"id": 1, "code": "01", "name": u"بانکها", "parent_id": 0, "lft": 1, "rgt": 2, "type": 2},
               {"id": 2, "code": "02", "name": u"هزینه ها", "parent_id": 0, "lft": 3, "rgt": 28, "type": 0},
               {"id": 3, "code": "03", "name": u"موجودیهای نقدی", "parent_id": 0, "lft": 29, "rgt": 32, "type": 2},
               {"id": 4, "code": "04", "name": u"بدهکاران / بستانکاران", "parent_id": 0, "lft": 33, "rgt": 34, "type": 2},
               {"id": 5, "code": "06", "name": u"تراز افتتاحیه", "parent_id": 0, "lft": 35, "rgt": 38, "type": 2},
               {"id": 6, "code": "13", "name": u"اسناد دریافتی", "parent_id": 0, "lft": 39, "rgt": 42, "type": 2},
               {"id": 7, "code": "07", "name": u"موجودی اول دوره", "parent_id": 0, "lft": 43, "rgt": 46, "type": 2},
               {"id": 8, "code": "12", "name": u"جاری شرکا", "parent_id": 0, "lft": 47, "rgt": 50, "type": 2},
               {"id": 9, "code": "09", "name": u"دارایی ثابت", "parent_id": 0, "lft": 51, "rgt": 52, "type": 2},
               {"id": 10, "code": "0201", "name": u"حقوق پرسنل", "parent_id": 2, "lft": 4, "rgt": 5, "type": 0},
               {"id": 11, "code": "0202", "name": u"آب", "parent_id": 2, "lft": 6, "rgt": 7, "type": 0},
               {"id": 12, "code": "0203", "name": u"برق", "parent_id": 2, "lft": 8, "rgt": 9, "type": 0},
               {"id": 13, "code": "0204", "name": u"تلفن", "parent_id": 2, "lft": 10, "rgt": 11, "type": 0},
               {"id": 14, "code": "0301", "name": u"صندوق", "parent_id": 3, "lft": 30, "rgt": 31, "type": 2},
               {"id": 15, "code": "0601", "name": u"-", "parent_id": 5, "lft": 36, "rgt": 37, "type": 2},
               {"id": 16, "code": "0701", "name": u"-", "parent_id": 7, "lft": 44, "rgt": 45, "type": 2},
               {"id": 17, "code": "10", "name": u"خرید", "parent_id": 0, "lft": 53, "rgt": 56, "type": 0},
               {"id": 18, "code": "11", "name": u"فروش", "parent_id": 0, "lft": 57, "rgt": 60, "type": 1},
               {"id": 19, "code": "1001", "name": u"-", "parent_id": 17, "lft": 54, "rgt": 55, "type": 0},
               {"id": 20, "code": "1101", "name": u"-", "parent_id": 18, "lft": 58, "rgt": 59, "type": 1},
               {"id": 21, "code": "08", "name": u"سرمایه اول دوره", "parent_id": 0, "lft": 61, "rgt": 64, "type": 2},
               {"id": 22, "code": "14", "name": u"اسناد پرداختی", "parent_id": 0, "lft": 65, "rgt": 68, "type": 2},
               {"id": 23, "code": "05", "name": u"درآمدهای متفرقه", "parent_id": 0, "lft": 69, "rgt": 76, "type": 1},
               {"id": 24, "code": "15", "name": u"تخفیفات نقدی خرید", "parent_id": 0, "lft": 77, "rgt": 80, "type": 2},
               {"id": 25, "code": "16", "name": u"تخفیفات نقدی فروش", "parent_id": 0, "lft": 81, "rgt": 84, "type": 2},
               {"id": 26, "code": "0205", "name": u"گاز", "parent_id": 2, "lft": 12, "rgt": 13, "type": 0},
               {"id": 27, "code": "0206", "name": u"تخفیفات - تعدیل حساب", "parent_id": 2, "lft": 14, "rgt": 15, "type": 0},
               {"id": 28, "code": "0207", "name": u"حمل", "parent_id": 2, "lft": 16, "rgt": 17, "type": 0},
               {"id": 29, "code": "0208", "name": u"ضایعات کالا", "parent_id": 2, "lft": 18, "rgt": 19, "type": 0},
               {"id": 30, "code": "0209", "name": u"عوارض شهرداری", "parent_id": 2, "lft": 20, "rgt": 21, "type": 0},
               {"id": 31, "code": "0210", "name": u"کارمزد بانک", "parent_id": 2, "lft": 22, "rgt": 23, "type": 0},
               {"id": 32, "code": "0211", "name": u"کرایه", "parent_id": 2, "lft": 24, "rgt": 25, "type": 0},
               {"id": 33, "code": "0212", "name": u"مالیات", "parent_id": 2, "lft": 26, "rgt": 27, "type": 0},
               {"id": 34, "code": "0501", "name": u"دریافت تخفیف بابت تعدیل حساب", "parent_id": 23, "lft": 70, "rgt": 71, "type": 1},
               {"id": 35, "code": "0502", "name": u"حق‌العمل", "parent_id": 23, "lft": 72, "rgt": 73, "type": 1},
               {"id": 36, "code": "0503", "name": u"متفرقه", "parent_id": 23, "lft": 74, "rgt": 75, "type": 1},
               {"id": 37, "code": "1201", "name": u"جاری شرکا", "parent_id": 8, "lft": 48, "rgt": 49, "type": 1},
               {"id": 38, "code": "17", "name": u"برگشت از خرید", "parent_id": 0, "lft": 85, "rgt": 88, "type": 2},
               {"id": 39, "code": "18", "name": u"برگشت از فروش", "parent_id": 0, "lft": 89, "rgt": 92, "type": 2},
               {"id": 40, "code": "1701", "name": u"-", "parent_id": 38, "lft": 86, "rgt": 87, "type": 2},
               {"id": 41, "code": "1801", "name": u"-", "parent_id": 39, "lft": 90, "rgt": 91, "type": 2},
               {"id": 42, "code": "1501", "name": u"-", "parent_id": 24, "lft": 78, "rgt": 79, "type": 2},
               {"id": 43, "code": "1601", "name": u"-", "parent_id": 25, "lft": 82, "rgt": 83, "type": 2},
               {"id": 44, "code": "1301", "name": u"-", "parent_id": 6, "lft": 40, "rgt": 41, "type": 2},
               {"id": 45, "code": "0801", "name": u"-", "parent_id": 21, "lft": 62, "rgt": 63, "type": 2},
               {"id": 46, "code": "1401", "name": u"-", "parent_id": 22, "lft": 66, "rgt": 67, "type": 2})
               
    logging.debug("upgrade to 1")
   

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    logging.debug("downgrade to 0")
