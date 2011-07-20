from amirconfig                 import config
from amir.database              import *
from sqlalchemy.sql.functions   import *

class Subjects():

    def __init__(self):
        pass
                
    def add(self, parentid, name, customercode=None, type=2):

        parent = config.db.session.query(Subject.code, Subject.lft).select_from(Subject).filter(Subject.id == parentid).first()

        #get left and right value
        sub_right = config.db.session.query(max(Subject.rgt)).select_from(Subject).filter(Subject.parent_id == parentid).first()
        sub_right = sub_right[0]

        if sub_right == None :
            sub_right = parent[1]
            
        #Update subjects which we want to place new subject before them:
        rlist = config.db.session.query(Subject).filter(Subject.rgt > sub_right).all()
        for r in rlist:
            r.rgt += 2
            config.db.session.add(r)
            
        llist = config.db.session.query(Subject).filter(Subject.lft > sub_right).all()
        for l in llist:
            l.lft += 2
            config.db.session.add(l)
            
        config.db.session.commit()

        sub_left  = sub_right + 1
        sub_right = sub_left + 1
        
        if customercode == None :
            #get customer code
            code = config.db.session.query(Subject.code).select_from(Subject).order_by(Subject.id.desc()).filter(Subject.parent_id == parentid).first()
            if code == None :
                customercode = "01"
            else :
                customercode = "%02d" % (int(code[0][-2:]) + 1)

        customercode = parent[0] + customercode

        mysubject = Subject(customercode, name, parentid, sub_left, sub_right, 2)
        config.db.session.add(mysubject)
        config.db.session.commit()
        
        query = config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == customercode)
        return query.first().id
