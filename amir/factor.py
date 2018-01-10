class factor:
    number = None # factor number
    bill_id = None
    trans_id = None
    dirty = False

    ## type of factor can be sell, buy
    facotr_type = "sell" 
    def __init__(self, number):
        if(number):
            print ' '
            #get bill_id and trans_id and type from database

    ## set current factor deatils
    #
    # @param detail dictionary contains details
    # \note keys:
    def set_detail(self, detail):
        self.type=type

    ## add a new product to list of products.
    #
    # it doesn't save to db you should call factor::save to save all products at once
    def add_product(self, product_id, count, price, discount, description):
        pass

    def add_noncash_peyment(self, cheque_id, description):
        pass

    ##save or update the factor row and set bill_id and transaction id and return factor number
    #
    # do not call any other function after save
    def save(self):
        pass

    ##return all factors
    def get_product(self):
        pass

    def get_noncash_peyment(self):
        pass

    ## return factor detail
    #
    # @return dictionary of details
    def get_detail(self, number=0):
        pass
