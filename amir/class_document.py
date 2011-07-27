import utility
from amirconfig import config
from database import Bill
from database import Notebook
from database import Subject

from datetime import date
from sqlalchemy.orm.util import outerjoin

class Document:
    def __init__(self, bill_number=0):
        self.bill_number = bill_number
        
        bill = self.get_bill()

        if bill:
            self.bill_id       = bill.id
            self.creation_date = bill.creation_date
            self.lastedit_date = bill.lastedit_date
            self.date          = bill.date
            self.permanent     = bill.permanent
        if not bill:
            self.bill_id       = 0
            self.creation_date = self.lastedit_date = self.date = date.today()      
            self.permanent     = False
            
        self.date_new = date.today()

    def get_bill_number(self):
        ''' returns bill number as string '''
        num = str(self.bill_number)
        if config.digittype == 1:
            return utility.convertToPersian(num)
        return num
    
    def __get_last_bill_number(self):
        query = config.db.session.query(Bill.number).select_from(Bill)
        last = query.order_by(Bill.number.desc()).first()
        if last != None:
            return last[0]
        return 0

    def get_bill(self, number=0):
        number = number or self.bill_number

        query = config.db.session.query(Bill)
        query = query.select_from(Bill)
        query = query.filter(Bill.number == number)
        return query.first()

    def get_notebook_rows(self):
        query = config.db.session.query(Notebook, Subject)
        query = query.select_from(outerjoin(Notebook, Subject, Notebook.subject_id == Subject.id))
        query = query.filter(Notebook.bill_id == self.bill_id)
        return query.all()

    def toggle_permanent(self, permanent):
        self.permanent = permanent

        query = config.db.session.query(Bill).select_from(Bill)
        bill = query.filter(Bill.id == self.bill_id).first()
        bill.permanent = self.permanent
        config.db.session.add(bill)
        config.db.session.commit()

    def delete(self):
        config.db.session.query(Notebook).filter(Notebook.bill_id == self.bill_id).delete()
        config.db.session.query(Bill).filter(Bill.id == self.bill_id).delete()
        config.db.session.commit()

    def add_bill(self):
        if self.bill_number == 0:
            self.bill_number = self.__get_last_bill_number() + 1

        bill = Bill (self.bill_number, self.creation_date, date.today(), self.date_new, False)
        config.db.session.add(bill)
        config.db.session.commit()
        self.bill_id = bill.id
        
    def add_notebook(self, subject_id, value, desctxt):
        row = Notebook (subject_id, self.bill_id, value, desctxt)
        config.db.session.add(row)
        # you should call config.db.session.commit() manually 
