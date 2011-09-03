from amirconfig import config
from database import Cheque
## \defgroup Controller
## @{

class ClassCheque:
    def __init__(self):
        self.new_cheques = []

    ##
    #
    # @return list of spendable cheques or None
    def get_spendable_cheques(self):
        pass

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
    def delete(self, id):
        pass

    # edit cheque
    # 
    # edit cheque and put last configs in database
    # @param info new configs as a dictionary
    def edit(self, info):
        pass

    ## get cheque id from cheque number
    #
    # @param number Cheque Serial Number
    # @return cheque id

    ## Add Cheque to db
    def add_cheque(self, amount, write_date, due_date, serial, status, customer_id, account_id, trans_id, notebook_id, desc):
        ch = Cheque(amount, write_date, due_date, serial, status, customer_id, account_id, trans_id, notebook_id, desc)
        self.new_cheques.append(ch)

    ## update cheque status
    #
    # updates cheque status and save last status in Cheque Histroy
    # \note You should call ClassCheque::save to save all changes or you will lose changes.
    # ChequeUI::save calls this function automatically.
    # @param id cheque id
    # @param status New status - Integer
    def update_status(self, id, status):
        pass

    ## Save datas to database
    def save(self):
        for cheque in self.new_cheques:
            config.db.session.add(cheque)

        config.db.session.commit()
## @}
