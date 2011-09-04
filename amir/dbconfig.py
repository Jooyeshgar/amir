import database
from amirconfig import config

## \defgroup Controller
## @{

class dbConfig:
    data = {
        'co-name':'Enter Company name',
        'co-logo':'',
        'custSubject'   : '4',
        'bank'          : '1',
        'cash'          :'14',
        'buy'           :'17', 
        'sell'          :'18', 
        'sell-discount' :'25',
        'tax'           :'33', 
        'partners'      : '8',
        'cost'          : '2',
        'bank-wage'     : '31',
        #"sell-adds": '7',
        #"fund": '9', 
        #"acc-receivable": '10', 
        #"commission": '11',
    }

    def get_default(self, key):
        try:
            return self.data[key]
        except KeyError:
            return ''

    def get_value(self, key):
        key = unicode(key)
        query = config.db.session.query(database.Config)
        query = query.filter(database.Config.cfgKey == key)
        return query.first().cfgValue

    def exists(self, key):
        query = config.db.session.query(database.Config)
        query = query.filter(database.Config.cfgKey == key)
        if query.first():
            return True
        return False
    
    def set_value(self, key, val, commit=True):
        val = unicode(val)
        query = config.db.session.query(database.Config)
        query = query.filter(database.Config.cfgId == key)
        query = query.update({u'cfgValue':val})
        if commit: # commit all of the at once for more speed
            config.db.session.commit()

    def add(self, key, mode, desc):
        if self.exists(key):
            raise Exception('Key already exists')
        
        row = database.Config(unicode(key), u'', unicode(desc), mode, 2)
        config.db.session.add(row)
        config.db.session.commit()

    def delete(self, id):
        query = config.db.session.query(database.Config).filter(database.Config.cfgId == id).first()
        config.db.session.delete(query)
        config.db.session.commit()
        
    def get_int(self ,key):
        try:
            return int(self.get_value(key))
        except ValueError:
            return None

    def get_int_list(self, key):
        val = []
        try:
            for item in self.get_value(key).split(','):
                if len(item) != 0:
                    val.append(int(item))
        except ValueError:
            return None
        return val

## @}
