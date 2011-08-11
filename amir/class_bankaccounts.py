from amirconfig import config
from database import BankAccounts
from database import BankNames

class BankAccountsClass:
    def __init__(self):
        pass

    def get_bank_names(self):
        return config.db.session.query(BankNames).select_from(BankNames).all()

    def add_account(self, name, number, type, owner, bank, branch, address, phone, webpage, desc):
        name    = unicode(name)
        owner   = unicode(owner)
        bank    = unicode(bank)
        branch  = unicode(branch)
        address = unicode(address)
        desc    = unicode(desc)

        query = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank).first()
        if query != None:
            bank_id = query.Id
        else:
            config.db.session.add(BankNames(bank))
            config.db.session.commit()
            bank_id = config.db.session.query(BankNames).select_from(BankNames).filter(BankNames.Name == bank).first().Id

        config.db.session.add(BankAccounts(name, number, type, owner, bank_id, branch, address, phone, webpage, desc))
        config.db.session.commit()

        return True
