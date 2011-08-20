import helpers

class ChequeUI:
    def __init__(self):
        self.builder = helpers.get_builder('cheque')
        self.builder.connect_signals(self)

    def list_selected_cheques(self):
        window = self.builder.get_object('list_cheque_window')
        window.show_all()

    def on_list_cheque_window_delete_event(self, window, event):
        window.hide_all()
        return True

    def on_add_cheque_window_delete_event(self, window, event):
        window.hide_all()
        return True

    def on_add_cheque_clicked(self, button):
        window = self.builder.get_object('add_cheque_window')
        window.show_all()
