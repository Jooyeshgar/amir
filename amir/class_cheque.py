from .share import share
from .database import Cheque
from .database import ChequeHistory
from .database import BankAccounts
from . import dbconfig
from . import class_subject
from . import dateentry
from sqlalchemy.orm.util import outerjoin

config = share.config

import sys
if sys.version_info > (3,):
    unicode = str

## \defgroup Controller
## @{

class ClassCheque:
    def __init__(self):
        self.new_cheques = []
        self.sp_cheques = []
    ##
    #
    # @return the cheque information by specefic id /masoud
    def get_cheque_info(self,id):
        ##id = unicode(id)
        ##return config.db.session.query(Cheque).select_from(Cheque).filter(Cheque.chqSerial == id).first()
        ##
        #
        # @return list of spendable cheques or None
        pass

    def get_spendable_cheques(self):
        li = config.db.session.query(Cheque,BankAccounts).select_from(outerjoin(Cheque,BankAccounts,Cheque.chqAccount == BankAccounts.accId)).filter(Cheque.chqStatus == 4).all()
        return li
    ## get the history of a single cheque
    #
    # @param id cheque id
    # @return histroy as a list
    def get_histroy(self, id):
        pass

    ## return all cheques from database
    def get_all_cheques(self):
        pass

    ## delete cheque from database
    #
    # only deletes from Cheque table. ChequeHistory will be updated cheque new status (deleted)
    def delete(self, serial):
        serial = unicode(serial)
        config.db.session.commit()
        id = config.db.session.query(Cheque).filter(Cheque.chqSerial == serial).first()
        id = id.chqId
        config.db.session.query(Cheque).filter(Cheque.chqId == id).delete()
        config.db.session.commit()

    # edit cheque
    #
    # edit cheque and put last configs in database
    # @param info new configs as a dictionary
    def edit(self, chequeC , chqId ,  ):
        cheque = config.db.session.query(Cheque).filter (chqId == chqId)
        cheque.chqAmount = chequeC.chqAmount
        cheque.chqWrtDate =chequeC. chqWrtDate
        cheque.chqDueDate =chequeC. chqDueDte
        cheque.chqSerial = chequeC.chqSerial
        #cheque.chqStatus = status           must edit from automatic accounting
        cheque.chqCust = chequeC.chqCust
        cheque.chqAccount = chequeC.chqAccount
        cheque.chqDesc = chequeC.chqDesc
        config.db.session.commit()
        self.new_cheques.append(chequeC)

    ## get cheque id from cheque number
    #
    # @param number Cheque Serial Number
    # @return cheque id

    ## Add Cheque to db
    def add_cheque(self, amount, write_date, due_date, serial, status, customer_id, account_id, trans_id, notebook_id, desc, bill_id, cheque_order):
        serial = unicode(serial)
        ch = Cheque(amount, write_date, due_date, serial, status, customer_id, account_id, trans_id, notebook_id, unicode(desc), None, bill_id, cheque_order)
        self.new_cheques.append(ch)

    ## update cheque status
    #
    # updates cheque status and save last status in Cheque Histroy
    # \note You should call ClassCheque::save to save all changes or you will lose changes.
    # ChequeUI::save calls this function automatically.
    # @param id cheque id
    # @param status New status - Integer
    # @param customer_id new customer Id
    def update_status(self, id,  status , customer_id):
        current_date = dateentry.DateEntry().getDateObject()
        ch = config.db.session.query(Cheque).filter(Cheque.chqId == id ).first()
        ch_history = ChequeHistory(ch.chqId, ch.chqAmount, ch.chqWrtDate, ch.chqDueDate, ch.chqSerial, status, customer_id, ch.chqAccount, ch.chqTransId, ch.chqDesc, current_date)
        config.db.session.add(ch_history)
        config.db.session.commit()
        ch.chqHistoryId = ch_history. Id
        ch.chqStatus = status
        ch.chqCust = customer_id

    ## Save datas to database
    def save(self):
        for cheque in self.new_cheques:
            config.db.session.add(cheque)
        config.db.session.commit()

    def save_cheque_history(self,current_date):
        for new_ch in self.new_cheques:
            ch = config.db.session.query(Cheque).filter(Cheque.chqSerial == new_ch.chqSerial).filter(Cheque.chqCust == new_ch.chqCust).first()
            ch_history = ChequeHistory(ch.chqId, ch.chqAmount, ch.chqWrtDate, ch.chqDueDate, ch.chqSerial, ch.chqStatus, ch.chqCust, ch.chqAccount, ch.chqTransId, ch.chqDesc, current_date)
            config.db.session.add(ch_history)
            config.db.session.commit()
            ch.chqHistoryId = ch_history. Id
       # for sp in self.sp_cheques:
          #  ch = config.db.session.query(Cheque).filter(Cheque.chqSerial == sp['serial']).first()
        config.db.session.commit()


## @}
