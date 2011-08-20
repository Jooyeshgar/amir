
## \defgroup Controller
## @{

class ClassCheque:
    def __init__(self):
        pass

    ##
    #
    # @return list of spendable cheques or None
    def get_spendable_cheques(self):
        pass

    ## Add Cheque to db
    def add_cheque(self):
        pass

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
        pass
## @}
