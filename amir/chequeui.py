import helpers

## \defgroup UserInterface
## @{

class ChequeUI:
    def __init__(self):
        ## A list contains information about new cheques
        self.new_cheques = []
        ## a list contains informations about selected cheques for spending
        self.spend_cheques = []

    ## list cheques you are going to add to database
    #
    # if you want to add a list of cheques (more than one) to database you should use this.
    # it shows a list of currently added cheques in a window.
    # there is an add button to append new cheques to the list.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    def list_new_cheques(self):
        pass

    ## list cheques you are going to spend
    #
    # if you want to spend a list of cheques (more than one) you should use this.
    # it shows a list of selected cheques in a window.
    # there is an add button to selected new cheques for spending.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    def list_spend_cheque(self):
        pass

    ## show histroy of cheque.
    #
    # there is a text entry in window so user can enter cheque id
    def show_history(self):
        pass

    ## Save datas to database.
    #
    # do not call any other function after this step.
    def save(self):
        pass

    ## add a new cheque
    #
    # if you want to add a single cheque use this, else using ChequeUI::list_new_cheques for multiple cheques is recommended.
    #
    # \note you can use ChequeUI::new_cheque for adding multiple cheques too. (call ChequeUI::new_cheque for each cheque)
    # You can use ChequeUI::list_new_cheques to list cheques before saving.
    #
    # <b>Signal</b> new_cheque_selected
    #
    # <b>Signal Handler</b> (Window, dictionary of items)
    # @return GtkWindow
    def new_cheque(self):
        pass

    ## select a cheque to spend
    #
    # shows a list available cheque for spending to selecting a single cheque from that list.
    # if you want to spend multiple cheques ChequeUI::list_spend_cheque is recommended.
    # \note see ChequeUI::new_cheque
    #
    # <b>Signal</b> spend_cheque_selected
    #
    # <b>Signal Handler</b> (Window)
    # Signal Handler (Window, cheque_id)
    # @return GtkWindow
    def spend_cheque(self):
        pass

## @}
