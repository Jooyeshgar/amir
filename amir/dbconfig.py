import  sys
import  os

import  utility

from    sqlalchemy.orm              import  sessionmaker, join
from    sqlalchemy.orm.util         import  outerjoin
from    sqlalchemy.sql              import  and_, or_
from    sqlalchemy.sql.functions    import  *

from    helpers                     import  get_builder
from    amirconfig                  import  config
from    datetime                    import  date
from    database                    import  *


class dbConfig:

    data = {
        'custSubject': '1',
        'bank'       : '2',
        'cash'       : '3',
        
        "buy": 4, 
        "sell": 5, 
        "sell-discount": 6,
        "sell-adds": 7,
        "tax": 8, 
        "fund": 9, 
        "acc-receivable": 10, 
        "commission": 11
    }

    def get_value(self, key):
        return self.data[key]
        
    def get_int(self ,key):
        return int(self.data[key])
