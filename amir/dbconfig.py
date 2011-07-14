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

    def __init__(self):
        data = {
            'custSubject': 1,
            'bank'       : 2
            }
        
    def GetValue(self ,key):
        return self.data[key]
