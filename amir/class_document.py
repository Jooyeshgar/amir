from amirconfig import config
from database import Bill
from database import Notebook
from database import Subject

from datetime import date
from sqlalchemy.orm.util import outerjoin

class Document:
    def __init__(self):
        self.id            = 0
        self.number        = 0
        self.creation_date = date.today()
        self.lastedit_date = date.today()
        self.date          = date.today()
        self.permanent     = False

        self.new_date      = date.today()
        self.notebooks     = []

    def set_bill(self, number):
        query = config.db.session.query(Bill)
        query = query.select_from(Bill)
        query = query.filter(Bill.number == number)
        bill  = query.first()
        
        if bill != None:
            self.id            = bill.id
            self.number        = bill.number
            self.creation_date = bill.creation_date
            self.lastedit_date = bill.lastedit_date
            self.date          = bill.date
            self.permanent     = bill.permanent
            return True
        return False
    
    def get_notebook_rows(self):
        query = config.db.session.query(Notebook, Subject)
        query = query.select_from(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id))
        query = query.filter(Notebook.bill_id == self.id)
        return query.all()

    def set_permanent(self, permanent):
        if self.id == 0:
            raise Exception('You should save the document before make it permanent')
        
        self.permanent = permanent
        query = config.db.session.query(Bill).select_from(Bill).filter(Bill.id == self.id)
        query.update({Bill.permanent:self.permanent})
        config.db.session.commit()

    def delete(self):
        config.db.session.query(Notebook).filter(Notebook.bill_id == self.id).delete()
        config.db.session.query(Bill).filter(Bill.id == self.id).delete()
        config.db.session.commit()
        
    def add_notebook(self, subject_id, value, desctxt):
        self.notebooks.append((subject_id, value, desctxt))
        
    def save(self):
        if len(self.notebooks) == 0:
            self.notebooks = []
            return -1
        
        sum = 0
        for notebook in self.notebooks:
            sum += notebook[1]
        if sum != 0:
            self.notebooks = []
            return -2
        
        if self.number > 0:
            self.delete()
        else:
            query = config.db.session.query(Bill.number).select_from(Bill)
            last = query.order_by(Bill.number.desc()).first()
            if last != None:
                self.number = last[0] + 1
            else:
                self.number = 1

        bill = Bill(self.number, self.creation_date, date.today(), self.new_date, False)
        config.db.session.add(bill)
        config.db.session.commit()
        
        query = config.db.session.query(Bill).select_from(Bill)
        query = query.filter(Bill.number == self.number)
        self.id = query.first().id
        
        for notebook in self.notebooks:
                config.db.session.add(Notebook(notebook[0], self.id, notebook[1], notebook[2]))

        config.db.session.commit()
        self.notebooks = []
        return True