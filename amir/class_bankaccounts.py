from amirconfig import config
from database import BankNames

class BankAccountsClass:
    def __init__(self):
        pass

    def get_bank_names(self):
        return config.db.session.query(BankNames).select_from(BankNames).all()
