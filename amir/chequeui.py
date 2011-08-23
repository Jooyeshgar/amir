import helpers

import gtk

## \defgroup UserInterface
## @{

class ChequeUI:
    def __init__(self):
        ## A list contains information about new cheques
        self.new_cheques = []
        ## a list contains informations about selected cheques for spending
        self.spend_cheques = []

        ## GtkBuilder for cheque widgets
        self.builder = helpers.get_builder('cheque')
        self.builder.connect_signals(self)

        w = self.builder.get_object('list_cheque_window').resize(400, 1)

    ## list cheques you are going to add/ or all cheques in database
    #
    # if you want to add a list of cheques (more than one) to database you should use this.
    # it shows a list of currently added cheques in a window.
    # there is an add button to append new cheques to the list.
    # remember to call ChequeUI::save to save to database or you will lose everything.
    # @param mode, 'all' -> all cheques, 'add'-> if you want to add cheques (used in automatic accounting)
    def list_cheques(self, mode):
        w = self.builder.get_object('list_cheque_window')
        w.set_position(gtk.WIN_POS_CENTER)
        w.set_modal(True)
        w.show_all()

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

    ## Signal Handler (When User Clicks On Add in list_cheque_window 
    def on_add_cheque_clicked(self, sender):
        w = self.builder.get_object('add_cheque_widnow')
        w.set_position(gtk.WIN_POS_CENTER)
        w.set_modal(True)
        w.show_all()

## @}
