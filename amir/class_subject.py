from .share import share
from amir.database import *
from sqlalchemy.sql.functions import *

# config = share.config

## \defgroup Controller
## @{


class Subjects():

    def __init__(self):
        pass

    # add a new subject
    # @param parentid: id of parrent subject, 0 for main
    # @param name: name of customer
    # @param code: customer code that can be none for auto increment
    # @param type: 0 for Debtor, 1 for Creditor, 2 for both
    def add(self, parentid, name, code=None, type=2):

        parent = share.config.db.session.query(Subject.code, Subject.lft).select_from(
            Subject).filter(Subject.id == parentid).first()

        # get left and right value
        sub_right = share.config.db.session.query(max(Subject.rgt)).select_from(
            Subject).filter(Subject.parent_id == parentid).first()
        sub_right = sub_right[0]

        if sub_right == None:
            sub_right = parent[1]

        # Update subjects which we want to place new subject before them:
        rlist = share.config.db.session.query(Subject).filter(
            Subject.rgt > sub_right).all()
        for r in rlist:
            r.rgt += 2
            share.config.db.session.add(r)

        llist = share.config.db.session.query(Subject).filter(
            Subject.lft > sub_right).all()
        for l in llist:
            l.lft += 2
            share.config.db.session.add(l)

        share.config.db.session.commit()

        sub_left = sub_right + 1
        sub_right = sub_left + 1

        if code == None:
            # get customer code
            code = share.config.db.session.query(Subject.code).select_from(Subject).order_by(
                Subject.id.desc()).filter(Subject.parent_id == parentid).first()
            if code == None:
                code = "001"
            else:
                code = "%03d" % (int(code[0][-3:]) + 1)

        code = parent[0] + code

        mysubject = Subject(code, name, parentid, sub_left, sub_right, 2)
        share.config.db.session.add(mysubject)
        share.config.db.session.commit()

        query = share.config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        return query.first().id

    def get_code(self, id):
        query = share.config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.id == id).first()
        if query == None:
            return str(id)
        else:
            return query.code

    def get_name(self, id):
        query = share.config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.id == id).first()
        if query == None:
            return str(id)
        else:
            return query.name

    def get_id(self, code):
        query = share.config.db.session.query(Subject).select_from(Subject)
        query = query.filter(Subject.code == code)
        return query.first().id

    # Get id from name of subject
    def get_id_from_name(self, name):
        query = share.config.db.session.query(Subject.id).select_from(Subject)
        query = query.filter(Subject.name == name)
        try:
            return query.first().id
        except:
            return 0

    # chek customer code is valid and exist.
    # @return: -1 for invalid, 1 for valid, 2 for exist
    def chek_code(self, code):
        if len(code) % 3 == 1:
            return -1
        query = share.config.db.session.query(Subject.id).select_from(
            Subject).filter(Subject.code == code).all()
        if len(query) == 0:
            return 1
        else:
            return 2

## @}
