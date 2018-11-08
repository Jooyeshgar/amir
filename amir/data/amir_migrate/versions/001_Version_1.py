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
from datetime import date

meta = MetaData()

#New tables (version 1):
subject = Table('subject', meta,
    Column('id', Integer, primary_key=True),
    Column('code', String(20), nullable=False),
    Column('name', Unicode(60), nullable=False),
    Column('parent_id', Integer, ColumnDefault(0), ForeignKey('subject.id')),
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
    from sqlalchemy.orm import sessionmaker, scoped_session
    meta.bind = migrate_engine
    Session = scoped_session(sessionmaker(bind=migrate_engine))
    session = Session()

    subject.create(checkfirst=True)
    bill.create(checkfirst=True)
    notebook.create(checkfirst=True)

    #Insert test data
    op = subject.insert()
    op.execute({"id": 1 , "code":"0"  , "name": "", "parent_id": None , "lft": 0 , "rgt": 1000  , "type":2})

    u = subject.update()
    u = u.values({"id": 0})
    u = u.where(subject.c.id == 1)
    session.execute(u)
    session.commit()
    
    op.execute(
				   # --------------------              
         #      {"id": 7 , "code":"07"  , "name": u"موجودی اول دوره"             , "parent_id": 0 , "lft": 43, "rgt": 46 , "type":2},                             			                                
        #       {"id": 16, "code":"0701", "name": u"-"                           , "parent_id": 7 , "lft": 44, "rgt": 45 , "type":2},
		#		{"id": 9 , "code":"09"  , "name": u"دارایی ثابت"                 , "parent_id": 0 , "lft": 51, "rgt": 52 , "type":2},			                  
         #      {"id": 21, "code":"08"  , "name": u"سرمایه اول دوره"             , "parent_id": 0 , "lft": 61, "rgt": 64 , "type":2},               
		#	   {"id": 45, "code":"0801", "name": u"-"                           , "parent_id": 21, "lft": 62, "rgt": 63 , "type":2},		               
			   # -------------------------------
			   
             #  {"id": 27, "code":"0206", "name": u"تخفیفات - تعدیل حساب"        , "parent_id": 2 , "lft": 14, "rgt": 15 , "type":0},               
              # {"id": 32, "code":"0211", "name": u"کرایه"                       , "parent_id": 2 , "lft": 24, "rgt": 25 , "type":0},               
              # {"id": 34, "code":"0501", "name": u"دریافت تخفیف بابت تعدیل حساب", "parent_id": 23, "lft": 70, "rgt": 71 , "type":1},
              # {"id": 35, "code":"0502", "name": u"حق‌العمل"                     , "parent_id": 23, "lft": 72, "rgt": 73 , "type":1},                             
			  
			   {"id": 1 , "code":"10"  , "name": u"بانکها"                      , "parent_id": 0 , "lft": 1 , "rgt": 2  , "type":2},
			   {"id": 2 , "code":"40"  , "name": u"هزینه ها"                    , "parent_id": 0 , "lft": 3 , "rgt": 28 , "type":0},
			   {"id": 3 , "code":"11"  , "name": u"موجودیهای نقدی"              , "parent_id": 0 , "lft": 29, "rgt": 32 , "type":2},
			   {"id": 4 , "code":"12"  , "name": u"بدهکاران/بستانکاران"      				, "parent_id": 0 , "lft": 33, "rgt": 34 , "type":2},  
			   {"id": 6 , "code":"13"  , "name": u"اسناد دریافتنی"              , "parent_id": 0 , "lft": 39, "rgt": 42 , "type":2},
               {"id": 10, "code":"4001", "name": u"حقوق پرسنل"                  , "parent_id": 2 , "lft": 4 , "rgt": 5  , "type":0},
               {"id": 11, "code":"4002", "name": u"آب"                          , "parent_id": 2 , "lft": 6 , "rgt": 7  , "type":0},
               {"id": 12, "code":"4003", "name": u"برق"                         , "parent_id": 2 , "lft": 8 , "rgt": 9  , "type":0},
               {"id": 13, "code":"4004", "name": u"تلفن"                        , "parent_id": 2 , "lft": 10, "rgt": 11 , "type":0},
			   {"id": 26, "code":"4005", "name": u"گاز"                         , "parent_id": 2 , "lft": 12, "rgt": 13 , "type":0},
			   {"id": 27, "code":"4006", "name": u"پست"                         , "parent_id": 2 , "lft": 16, "rgt": 17 , "type":0},
			   {"id": 28, "code":"4007", "name": u"هزینه حمل"                         , "parent_id": 2 , "lft": 16, "rgt": 17 , "type":0},
			   {"id": 29, "code":"4008", "name": u"ضایعات کالا"                  , "parent_id": 2 , "lft": 18, "rgt": 19 , "type":0},
               {"id": 30, "code":"4009", "name": u"عوارض شهرداری"               , "parent_id": 2 , "lft": 20, "rgt": 21 , "type":0},
               {"id": 31, "code":"4010", "name": u"کارمزد بانک"                 , "parent_id": 2 , "lft": 22, "rgt": 23 , "type":0},
			   {"id": 33, "code":"4011", "name": u"مالیات"                      , "parent_id": 2 , "lft": 26, "rgt": 27 , "type":0},
			   {"id": 34, "code":"4011", "name": u"هزینه اجاره محل"                      , "parent_id": 2 , "lft": 26, "rgt": 27 , "type":0},
			   {"id": 32, "code":"4012", "name": u"هزینه های متفرقه"            , "parent_id": 2 , "lft": 26, "rgt": 27 , "type":0},
               {"id": 14, "code":"1101"  , "name": u"صندوق"                     , "parent_id": 3 , "lft": 30, "rgt": 31 , "type":2},			   
			   {"id": 59, "code":"1102", "name": u"تنخواه گردانها"              , "parent_id": 3 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 58 , "code":"1201"  , "name": u"اشخاص متفرقه"      		, "parent_id": 4 , "lft": 33, "rgt": 34 , "type":2},  
			   {"id": 44, "code":"1301", "name": u"اسناد دریافتنی"              , "parent_id": 6 , "lft": 40, "rgt": 41 , "type":2},			   			              			                                                                           
               
			   {"id": 67, "code":"14"  , "name": u"اسناد در جریان وصول"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 68, "code":"1401", "name": u"اسناد در جریان وصول"                , "parent_id": 67 , "lft": 30, "rgt": 31 , "type":2},
			   
			   {"id": 69, "code":"15", "name": u"موجودی مواد و کالا"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 7, "code":"1501", "name": u"موجودی مواد اولیه"                , "parent_id": 69 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 70, "code":"1502", "name": u"موجودی مواد و کالا"                , "parent_id": 69 , "lft": 30, "rgt": 31 , "type":2},
			   
			   {"id": 71, "code":"16"  , "name": u"پیش پرداخت ها"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 72, "code":"1601", "name": u"پیش پرداخت مالیات"                , "parent_id": 71 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 73, "code":"1602", "name": u"پیش پرداخت اجاره"                , "parent_id": 71 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 74, "code":"1603", "name": u"پیش پرداخت هزینه های جاری"                , "parent_id": 71 , "lft": 30, "rgt": 31 , "type":2},
			          
			   {"id": 75, "code":"17", "name": u"دارایی های غیر جاری"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 76, "code":"1701", "name": u"اموال، ماشین آلات و تجهیزات"       , "parent_id": 75 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 77, "code":"1702", "name": u"استهلاک انباشته اموال، ماشین آلات و تجهیزات"                , "parent_id": 75 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 78, "code":"1703", "name": u"سرمایه گذاری های بلند مدت"        , "parent_id": 75 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 79, "code":"1704", "name": u"سپرده ها و مطالبات بلندمدت"                , "parent_id": 75 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 80, "code":"1705", "name": u"سایر دارایی ها"               , "parent_id": 75 , "lft": 30, "rgt": 31 , "type":2},
			   
			   {"id": 38, "code":"18"  , "name": u"سایر حسابهای دریافتنی"       , "parent_id": 0 , "lft": 89, "rgt": 94 , "type":2},
               {"id": 40, "code":"1801", "name": u"مالیات بر ارزش افزوده خرید"     , "parent_id": 38, "lft": 90, "rgt": 91 , "type":2},
               {"id": 56, "code":"1802", "name": u"عوارض خرید"                  , "parent_id": 38, "lft": 92, "rgt": 93 , "type":2},
               {"id": 62, "code":"1803", "name": u"مساعده حقوق"  				, "parent_id": 38 , "lft": 89, "rgt": 94 , "type":2},
               {"id": 63, "code":"1804", "name": u"جاری کارکنان"  				, "parent_id": 38 , "lft": 89, "rgt": 94 , "type":2},
               {"id": 64, "code":"1805", "name": u"حق بیمه 5درصد مکسوره از صورت وضعیت"  , "parent_id": 38 , "lft": 89, "rgt": 94 , "type":2},			   
			   
			   {"id": 22, "code":"20"  , "name": u"اسناد پرداختنی"              , "parent_id": 0 , "lft": 65, "rgt": 68 , "type":2},
               {"id": 46, "code":"2001", "name": u"اسناد پرداختنی"              , "parent_id": 22, "lft": 66, "rgt": 67 , "type":2},    
               
			     

			   {"id": 81, "code":"22", "name": u"پیش دریافت ها"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 82, "code":"2201", "name": u"پیش دریافت فروش محصولات"                , "parent_id": 81 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 83, "code":"2202", "name": u"سایر پیش دریافت ها"                , "parent_id": 81 , "lft": 30, "rgt": 31 , "type":2},
			   			   
				{"id": 39, "code":"23"  , "name": u"سایر حسابهای پرداختنی"       , "parent_id": 0 , "lft": 95, "rgt": 100, "type":2},
               {"id": 41, "code":"2301", "name": u"مالیات بر ارزش افزوده فروش"     , "parent_id": 39, "lft": 96, "rgt": 97 , "type":2},
			   {"id": 57, "code":"2302", "name": u"عوارض فروش"                  , "parent_id": 39, "lft": 98, "rgt": 99 , "type":2},
               {"id": 66, "code":"2303"  , "name": u"عیدی و پاداش پرداختنی"       , "parent_id": 39 , "lft": 95, "rgt": 100, "type":2},    
		   
			   {"id": 84, "code":"30", "name": u"حقوق صاحبان سهام"                , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 21, "code":"3001", "name": u"سرمایه"                , "parent_id": 84 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 85, "code":"3002", "name": u"اندوخته قانونی"                , "parent_id": 84 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 86, "code":"3003", "name": u"سود (زیان) انباشته"                , "parent_id": 84 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 96, "code":"3004", "name": u"سود (زیان) جاری"                , "parent_id": 84 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 87, "code":"3005", "name": u"تقسیم سود"                , "parent_id": 84 , "lft": 30, "rgt": 31 , "type":2},
			   
	
			   {"id": 88, "code":"41", "name": u"قیمت تمام شده کالای فروش رفته"  , "parent_id": 0 , "lft": 30, "rgt": 31 , "type":2},
			   {"id": 89, "code":"4101", "name": u"قیمت تمام شده کالای فروش رفته"  , "parent_id": 88 , "lft": 30, "rgt": 31 , "type":2},
			    	
               {"id": 23, "code":"50"  , "name": u"درآمدها"             , "parent_id": 0 , "lft": 69, "rgt": 76 , "type":1},
			   {"id": 36, "code":"5001", "name": u"درآمد متفرقه"                      , "parent_id": 23, "lft": 74, "rgt": 75 , "type":1},
			   
			   {"id": 18, "code":"60"  , "name": u"فروش"                        , "parent_id": 0 , "lft": 57, "rgt": 60 , "type":1},
			   {"id": 20, "code":"6001", "name": u"فروش"                        , "parent_id": 18, "lft": 58, "rgt": 59 , "type":1},
			   
			   {"id": 25, "code":"61"  , "name": u"برگشت از فروش و تخفیفات"     , "parent_id": 0 , "lft": 83, "rgt": 88 , "type":2},
			   {"id": 55, "code":"6101", "name": u"تخفیفات فروش"                , "parent_id": 25, "lft": 86, "rgt": 87 , "type":2},
			   {"id": 43, "code":"6102", "name": u"برگشت از فروش"                , "parent_id": 25, "lft": 86, "rgt": 87 , "type":2},
			   
			   {"id": 17, "code":"62"  , "name": u"خرید"                        , "parent_id": 0 , "lft": 53, "rgt": 56 , "type":0},
               {"id": 19, "code":"6201", "name": u"خرید"                        , "parent_id": 17, "lft": 54, "rgt": 55 , "type":0},
			   
			   {"id": 24, "code":"63"  , "name": u"برگشت از خرید و تخفیفات"     , "parent_id": 0 , "lft": 77, "rgt": 82 , "type":2},
			   {"id": 42, "code":"6301", "name": u"برگشت از خرید"                , "parent_id": 24, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 53, "code":"6302", "name": u"تخفیفات خرید"                , "parent_id": 24, "lft": 80, "rgt": 81 , "type":2},
			   
			   {"id": 90, "code":"64", "name": u"حسابهای انتظامی"                , "parent_id": 0, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 91, "code":"6401", "name": u"حسابهای انتظامی به نفع شرکت"   , "parent_id": 90, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 92, "code":"6402", "name": u"حسابهای انتظامی به عهده شرکت"  , "parent_id": 90, "lft": 80, "rgt": 81 , "type":2},
			   
			   {"id": 93, "code":"65", "name": u"طرف حسابهای انتظامی"            , "parent_id": 0, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 94, "code":"6502", "name": u"طرف حساب انتظامی به نفع شرکت"  , "parent_id": 93, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 95, "code":"6502", "name": u"طرف حساب انتظامی به عهده شرکت"  , "parent_id": 93, "lft": 80, "rgt": 81 , "type":2},
			   			   
			   {"id": 97, "code":"66", "name": u"تخفیفات نقدی"                  , "parent_id": 0, "lft": 80, "rgt": 81 , "type":2},
			   {"id": 98, "code":"6601", "name": u"تخفیفات نقدی"                , "parent_id": 97, "lft": 80, "rgt": 81 , "type":2},

			   {"id": 5 , "code":"67"  , "name": u"تراز افتتاحیه"               , "parent_id": 0 , "lft": 35, "rgt": 38 , "type":2}, 
			   {"id": 15, "code":"6701", "name": u"تراز افتتاحیه"               , "parent_id": 5 , "lft": 36, "rgt": 37 , "type":2},
			   
			   {"id": 8 , "code":"68"  , "name": u"جاری شرکا"                   , "parent_id": 0 , "lft": 47, "rgt": 50 , "type":2},
			   {"id": 37, "code":"6801", "name": u"جاری شرکا"                   , "parent_id": 8 , "lft": 48, "rgt": 49 , "type":1},
			   ) 


   # bill = Table('bill' , meta , autoload = True)
    op = bill.insert()
    op.execute({'id':1 , 'number':1 , 'creation_date' : date.today() , 'lastedit_date': date.today() , 'date': date.today(), 'permanent':True  })
    
    logging.debug("upgrade to 1")
   

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    logging.debug("downgrade to 0")
