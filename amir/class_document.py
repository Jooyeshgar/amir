from amirconfig import config
from database import Bill
from database import Notebook
from database import Subject
from database import Cheque
from database import ChequeHistory

from datetime import date
from sqlalchemy.orm.util import outerjoin

## \defgroup Controller
## @{

class Document:
    def __init__(self):
        self.id            = 0
        self.number        = 0
        self.creation_date = date.today()
        self.lastedit_date = date.today()
        self.date          = date.today()
        self.permanent     = False

        self.new_date = date.today()
        self.notebooks = []
        self.cheques = []
        self.spend_cheques = []
        self.cheques_result = {}

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
        
    def add_notebook(self, subject_id, value, desctxt, id=None):
        self.notebooks.append((subject_id, value, desctxt ,id))
    
    def clear_notebook(self):
        self.notebooks = []
        self.cheques = []
        self.cheques_result = {}

    def add_cheque(self, subject_id, value, desctxt, cheque_id):
        self.cheques.append((subject_id, float(value), desctxt, cheque_id))
        self.cheques_result[cheque_id] = None
    
        
    def save(self,delete_items=None):
        if len(self.notebooks) == 0:
            self.notebooks = []
            return -1

        sum = 0
        for notebook in self.notebooks:
            sum += notebook[1]
        for cheque in self.cheques:
            sum += cheque[1]
        if sum != 0:
            self.notebooks = []
            return -2
        
        if self.number > 0:
            bill = config.db.session.query(Bill).select_from(Bill)
            notebooks = config.db.session.query(Notebook).select_from(Notebook)
            bill = bill.filter(Bill.number == self.number).first()
            bill.lastedit_date = date.today()
            notebook_ides = []
            for notbook in self.notebooks:
                
                if notbook[3] == 0:
                    config.db.session.add(Notebook(notbook[0], self.id, notbook[1], notbook[2]))
                else:
                    temp = None
                    temp = notebooks.filter(Notebook.id == notbook[3]).first()
                    temp.subject_id = notbook[0]
                    temp.desc = notbook[2]
                    temp.value = notbook[1]
                    temp_2 = None
                    temp_2 = config.db.session.query(Cheque).select_from(Cheque).filter(Cheque.chqNoteBookId == notbook[3]).first()
                    if temp_2 != None:
                        temp_2.chqAmount = abs(notbook[1])
                        temp_2.chqDesc = notbook[2]
                        cheque_his = ChequeHistory(temp_2.chqId,temp_2.chqAmount,temp_2.chqWrtDate,temp_2.chqDueDate,temp_2.chqSerial,temp_2.chqStatus
                                                            , temp_2.chqCust, temp_2.chqAccount, temp_2.chqTransId, temp_2.chqDesc , date.today())
                        config.db.session.add(cheque_his)
            for deletes in delete_items:
                config.db.session.query(Notebook).filter(Notebook.id == deletes).delete()
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

            for cheque in self.cheques:
                n = Notebook(cheque[0], self.id, cheque[1], cheque[2])
                config.db.session.add(n)
                config.db.session.commit()
                self.cheques_result[cheque[3]] = n.id

        self.notebooks = []
        config.db.session.commit()
        return self.id

    def get_error_message(self, code):
        if   code == -1:
            return "add some notebook items"
        elif code == -2:
            return "transation sum should be 0"

## @}
