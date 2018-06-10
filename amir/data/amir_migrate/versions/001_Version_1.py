#!/usr/bin/python2
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
    Column('type', Integer),
	mysql_charset='utf8'
)

bill = Table('bill', meta,
    Column('id', Integer, primary_key=True),
    Column('number', Integer, nullable = False),
    Column('creation_date', Date, nullable = False),
    Column('lastedit_date', Date, nullable = False),
    Column('date', Date, nullable = False),
    Column('permanent', Boolean, ColumnDefault(False), nullable = False),
	mysql_charset='utf8'
)

notebook = Table('notebook', meta,
    Column('id', Integer, primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id')),
    Column('bill_id', Integer, ForeignKey('bill.id')),
    Column('desc', UnicodeText, ColumnDefault("")),
    Column('value', Integer, ColumnDefault(0), nullable = False),
	mysql_charset='utf8'
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
    op.execute({"id": 1 , "code":"001"   , "name": u"بانکها"                      , "parent_id": 0 , "lft": 0 , "rgt":0 , "type":2},
               {"id": 2 , "code":"002"   , "name": u"هزینه ها"                    , "parent_id": 0 , "lft": 0 , "rgt":0 , "type":0},
               {"id": 3 , "code":"003"   , "name": u"موجودیهای نقدی"              , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 4 , "code":"004"   , "name": u"بدهکاران / بستانکاران"       , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 5 , "code":"006"   , "name": u"تراز افتتاحیه"               , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 6 , "code":"013"   , "name": u"اسناد دریافتی"               , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 7 , "code":"007"   , "name": u"موجودی اول دوره"             , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 8 , "code":"012"   , "name": u"جاری شرکا"                   , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 9 , "code":"009"   , "name": u"دارایی ثابت"                 , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 10, "code":"002001", "name": u"حقوق پرسنل"                  , "parent_id": 2 , "lft": 0 , "rgt":0 , "type":0},
               {"id": 11, "code":"002002", "name": u"آب"                          , "parent_id": 2 , "lft": 0 , "rgt":0 , "type":0},
               {"id": 12, "code":"002003", "name": u"برق"                         , "parent_id": 2 , "lft": 0 , "rgt":0 , "type":0},
               {"id": 13, "code":"002004", "name": u"تلفن"                        , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 14, "code":"003001", "name": u"صندوق"                       , "parent_id": 3 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 15, "code":"006001", "name": u"-"                           , "parent_id": 5 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 16, "code":"007001", "name": u"-"                           , "parent_id": 7 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 17, "code":"010"   , "name": u"خرید"                        , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 18, "code":"011"   , "name": u"فروش"                        , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":1},
               {"id": 19, "code":"010001", "name": u"-"                           , "parent_id": 17, "lft": 0, "rgt": 0 , "type":0},
               {"id": 20, "code":"011001", "name": u"-"                           , "parent_id": 18, "lft": 0, "rgt": 0 , "type":1},
               {"id": 21, "code":"008"   , "name": u"سرمایه اول دوره"             , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 22, "code":"014"   , "name": u"اسناد پرداختی"               , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 23, "code":"005"   , "name": u"درآمدهای متفرقه"             , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":1},
               {"id": 24, "code":"015"   , "name": u"برگشت از خرید و تخفیفات"     , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 25, "code":"016"   , "name": u"برگشت از فروش و تخفیفات"     , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 26, "code":"002005", "name": u"گاز"                         , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 27, "code":"002006", "name": u"تخفیفات - تعدیل حساب"        , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 28, "code":"002007", "name": u"حمل"                         , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 29, "code":"002008", "name": u"ضایعات کالا"                 , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 30, "code":"002009", "name": u"عوارض شهرداری"               , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 31, "code":"002010", "name": u"کارمزد بانک"                 , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 32, "code":"002011", "name": u"کرایه"                       , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 33, "code":"002012", "name": u"مالیات"                      , "parent_id": 2 , "lft": 0, "rgt": 0 , "type":0},
               {"id": 34, "code":"005001", "name": u"دریافت تخفیف بابت تعدیل حساب", "parent_id": 23, "lft": 0, "rgt": 0 , "type":1},
               {"id": 35, "code":"005002", "name": u"حق‌العمل"                     , "parent_id": 23, "lft": 0, "rgt": 0 , "type":1},
               {"id": 36, "code":"005003", "name": u"متفرقه"                      , "parent_id": 23, "lft": 0, "rgt": 0 , "type":1},
               {"id": 37, "code":"012001", "name": u"جاری شرکا"                   , "parent_id": 8 , "lft": 0, "rgt": 0 , "type":1},
               {"id": 38, "code":"017"   , "name": u"سایر حسابهای دریافتنی"       , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 39, "code":"018"   , "name": u"سایر حسابهای پرداختنی"       , "parent_id": 0 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 40, "code":"017001", "name": u"مالیات ارزش افزوده خرید"     , "parent_id": 38, "lft": 0, "rgt": 0 , "type":2},
               {"id": 41, "code":"018001", "name": u"مالیات ارزش افزوده فروش"     , "parent_id": 39, "lft": 0, "rgt": 0 , "type":2},
               {"id": 42, "code":"015001", "name": u"برگشت از خرید"               , "parent_id": 24, "lft": 0, "rgt": 0 , "type":2},
               {"id": 43, "code":"016001", "name": u"برگشت از فروش"               , "parent_id": 25, "lft": 0, "rgt": 0 , "type":2},
               {"id": 44, "code":"013001", "name": u"-"                           , "parent_id": 6 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 45, "code":"008001", "name": u"-"                           , "parent_id": 21, "lft": 0, "rgt": 0 , "type":2},
               {"id": 46, "code":"014001", "name": u"-"                           , "parent_id": 22, "lft": 0, "rgt": 0 , "type":2},
               {"id": 53, "code":"015002", "name": u"تخفیفات خرید"                , "parent_id": 24, "lft": 0, "rgt": 0 , "type":2},
               {"id": 55, "code":"016002", "name": u"تخفیفات فروش"                , "parent_id": 25, "lft": 0, "rgt": 0 , "type":2},
               {"id": 56, "code":"017002", "name": u"عوارض خرید"                  , "parent_id": 38, "lft": 0, "rgt": 0 , "type":2},
               {"id": 57, "code":"018002", "name": u"عوارض فروش"                  , "parent_id": 39, "lft": 0, "rgt": 0 , "type":2},
               {"id": 58, "code":"002013", "name": u"مشکوک الوصول"                , "parent_id": 2,  "lft": 0, "rgt": 0 , "type":1},
               {"id": 59, "code":"013002", "name": u"اسناد دریافتی"               , "parent_id": 6 , "lft": 0, "rgt": 0 , "type":2},
               {"id": 60, "code":"014003", "name": u"اسناد پرداختی"               , "parent_id": 22, "lft": 0, "rgt": 0 , "type":2})

    logging.debug("upgrade to 1")
   

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    logging.debug("downgrade to 0")
