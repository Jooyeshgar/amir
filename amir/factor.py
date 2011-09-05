class factor:
    number = None # factor number
    bill_id = None
    trans_id = None
    dirty = False
    facotr_type = "sell" # type of factor can be sell, buy, ...

    def __init__(self, number):
        if(number)
            #get bill_id and trans_id and type from database

    def set_detail(self, detail)
        self.type=type

    def add_product(self, product_id, count, price, discount, description)
        pass

    def add_noncash_peyment(self, cheque_id, description)
        pass

    ##save or update the factor row and set bill_id and transaction id and return factor number
    def save(self)
        pass

    ##return all factor rows
    def get_product(self)
        pass

    def get_noncash_peyment(self)
        pass

    ##return factor detail
    def get_detail(self, number=0)
        pass
