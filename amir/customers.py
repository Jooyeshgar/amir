import gobject

#import  warehousing
from . import class_subject
from . import decimalentry
from . import numberentry
from . import dateentry
from . import subjects
from . import customergroup
from . import utility
from .dbconfig import dbconf

from sqlalchemy.orm import sessionmaker, join
from sqlalchemy.orm.util import outerjoin
from sqlalchemy.sql import and_, or_
from sqlalchemy.sql.functions import *

from .helpers import get_builder
from .share import share
from datetime import date
from .database import *
import gi
from gi.repository import Gtk, GObject

from gettext import gettext as _

gi.require_version('Gtk', '3.0')
# config = share.config

## \defgroup UserInterface
## @{

## Register or edit a customer and create a subject row


class Customer(customergroup.Group):

    def __init__(self):
        customergroup.Group.__init__(self)

        self.custgrpentry = numberentry.NumberEntry(10)
        self.builder.get_object("custGrpBox").add(self.custgrpentry)
        self.custgrpentry.show()

        self.custIntroducerEntry = numberentry.NumberEntry(10)
        self.builder.get_object("custIntroducerBox").add(
            self.custIntroducerEntry)
        self.custIntroducerEntry.show()

        self.boxCommissionRateEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxCommissionRateEntry").add(
            self.boxCommissionRateEntry)
        self.boxCommissionRateEntry.show()

        self.boxDiscRateEntry = decimalentry.DecimalEntry(10)
        self.builder.get_object("boxDiscRateEntry").add(self.boxDiscRateEntry)
        self.boxDiscRateEntry.show()

    # show list of customer

    def viewCustomers(self, readonly=False):
        self.window = self.builder.get_object("viewCustomersWindow")
        if readonly:
            self.costmenu = self.builder.get_object("customersToolbar")
            self.costmenu.hide()

        self.treeview = self.builder.get_object("customersTreeView")
        self.treestore = Gtk.TreeStore(str, str, str, str, str)
        self.treestore.clear()
        self.treeview.set_model(self.treestore)

        column = Gtk.TreeViewColumn(_("Code"), Gtk.CellRendererText(), text=0)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Name"), Gtk.CellRendererText(), text=1)
        column.set_spacing(5)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        column.set_sort_indicator(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Debt"), Gtk.CellRendererText(), text=2)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Credit"), Gtk.CellRendererText(), text=3)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn(
            _("Balance"), Gtk.CellRendererText(), text=4)
        column.set_spacing(5)
        column.set_resizable(True)
        self.treeview.append_column(column)

        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        #self.treestore.set_sort_func(0, self.sortGroupIds)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        # Fill groups treeview
        query = share.config.db.session.query(CustGroups, Customers)
        query = query.select_from(
            outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
        query = query.order_by(CustGroups.custGrpId.asc())
        result = query.all()

        # Fill groups treeview
        query = share.config.db.session.query(Notebook)
        notes = query.all()
        creditNote = {}
        debtNote = {}
        for n in notes:
            if n.value > 0:
                try:
                    creditNote[n.subject_id] += n.value
                except KeyError:
                    creditNote[n.subject_id] = n.value
            else:
                try:
                    debtNote[n.subject_id] += n.value
                except KeyError:
                    debtNote[n.subject_id] = n.value

        last_gid = 0
        grouprow = None
        for g, c in result:
            if g.custGrpId != last_gid:
                grouprow = self.treestore.append(None, (utility.readNumber(
                    g.custGrpCode), utility.readNumber(g.custGrpName), "", "", ""))
                last_gid = g.custGrpId
            if c != None:
                try:
                    credit = creditNote[c.custSubj]
                except KeyError:
                    credit = 0
                try:
                    debt = abs(debtNote[c.custSubj])
                except KeyError:
                    debt = 0
                balance = credit - debt
                if balance < 0:
                    showBalance = "(" + utility.LN(abs(balance)) + ")"
                else:
                    showBalance = utility.LN(balance)
                self.treestore.append(grouprow, (utility.readNumber(c.custCode), str(c.custName),
                    utility.LN(debt), utility.LN(credit), showBalance))

        self.window.show_all()

    # Show add customers window
    def addNewCustomer(self, sender, pcode=""):
        self.editCustomer = False

        self.customerForm = self.builder.get_object("customersWindow")
        self.customerForm.set_title(_("Add New Customer"))
        self.builder.get_object(
            "addCustSubmitBtn").set_label(_("Add Customer"))

        query = share.config.db.session.query(
            Subject.code).order_by(Subject.id.desc())
        code = query.filter(Subject.parent_id ==
                            dbconf.get_int('custSubject')).first()
        if code == None:
            lastcode = "001"
        else:
            lastcode = "%03d" % (int(code[0][-2:]) + 1)
        self.builder.get_object("custCodeEntry").set_text(utility.LN(lastcode))
        # self.custgrpentry.set_text("")
        self.builder.get_object("custNameEntry").set_text("")
        self.builder.get_object("custEcnmcsCodeEntry").set_text("")
        self.builder.get_object("custPrsnalCodeEntry").set_text("")

        self.builder.get_object("custPhoneEntry").set_text("")
        self.builder.get_object("custCellEntry").set_text("")
        self.builder.get_object("custFaxEntry").set_text("")
        self.builder.get_object("custWebPageEntry").set_text("")
        self.builder.get_object("custEmailEntry").set_text("")
        self.builder.get_object("custRepViaEmailChk").get_active()
        self.builder.get_object("custAddressEntry").set_text("")
        self.builder.get_object("cusPostalCodeEntry").set_text("")

        self.builder.get_object("callResponsibleEntry").set_text("")
        self.builder.get_object("custConnectorEntry").set_text("")

        self.builder.get_object("custDescEntry").set_text("")
        # ----------------------------------
        self.builder.get_object("custTypeBuyerChk").set_active(True)
        self.builder.get_object("custTypeSellerChk").set_active(True)
        self.builder.get_object("custTypeMateChk").set_active(False)
        self.builder.get_object("custTypeAgentChk").set_active(False)
        self.custIntroducerEntry.set_text("")
        self.boxCommissionRateEntry.set_text("")
        self.boxDiscRateEntry.set_text("")
        self.builder.get_object("markedChk").set_active(False)
        self.builder.get_object("markedReasonEntry").set_text("")
        # ----------------------------------
        self.builder.get_object("custAccName1Entry").set_text("")
        self.builder.get_object("custAccNo1Entry").set_text("")
        self.builder.get_object("custAccBank1Entry").set_text("")
        self.builder.get_object("custAccName2Entry").set_text("")
        self.builder.get_object("custAccNo2Entry").set_text("")
        self.builder.get_object("custAccBank2Entry").set_text("")

        self.customerForm.show_all()

    def customerFormCanceled(self, sender=0, ev=0):
        self.customerForm.hide()
        return True

    def customerFormOkPressed(self, sender=0, ev=0):
        result = self.saveCustomer()
        if result == 0:
            self.customerForm.hide()

    def on_markedChk_toggled(self, sender=0, ev=0):
        self.builder.get_object("markedReasonEntry").set_sensitive(
            self.builder.get_object("markedChk").get_active())
#
#    def submitEditCust(self):
#        print "SUBMIT  EDIT"
#
    # save customer to database
    # @return: -1 on error, 0 for success

    def saveCustomer(self):
        custCode = utility.convertToLatin(
            self.builder.get_object("custCodeEntry").get_text())
        custGrp = self.custgrpentry.get_int()
        custName = self.builder.get_object("custNameEntry").get_text()
        custEcnmcsCode = self.builder.get_object("custEcnmcsCodeEntry").get_text()
        custPersonalCode = self.builder.get_object("custPrsnalCodeEntry").get_text()

        custPhone = self.builder.get_object("custPhoneEntry").get_text()
        custCell = self.builder.get_object("custCellEntry").get_text()
        custFax = self.builder.get_object("custFaxEntry").get_text()
        custWebPage = self.builder.get_object("custWebPageEntry").get_text()
        custEmail = self.builder.get_object("custEmailEntry").get_text()
        custRepViaEmail = self.builder.get_object("custRepViaEmailChk").get_active()
        custAddress = self.builder.get_object("custAddressEntry").get_text()
        custPostalCode = self.builder.get_object("cusPostalCodeEntry").get_text()

        callResponsible = self.builder.get_object("callResponsibleEntry").get_text()
        custConnector = self.builder.get_object("custConnectorEntry").get_text()

        custDesc = self.builder.get_object("custDescEntry").get_text()
        # ----------------------------------
        custTypeBuyer = self.builder.get_object(
            "custTypeBuyerChk").get_active()
        custTypeSeller = self.builder.get_object(
            "custTypeSellerChk").get_active()
        custTypeMate = self.builder.get_object("custTypeMateChk").get_active()
        custTypeAgent = self.builder.get_object(
            "custTypeAgentChk").get_active()
        custIntroducer = self.custIntroducerEntry.get_int()
        custCommission = self.boxCommissionRateEntry.get_float()
        custDiscRate = self.boxDiscRateEntry.get_float()
        custMarked = self.builder.get_object("markedChk").get_active()
        custReason = self.builder.get_object("markedReasonEntry").get_text()
        # ----------------------------------
        # custBalance         = self.boxBalanceEntry.get_float()
        # custCredit          = self.boxCreditEntry.get_float()
        custAccName1 = self.builder.get_object("custAccName1Entry").get_text()
        custAccNo1 = self.builder.get_object("custAccNo1Entry").get_text()
        custAccBank1 = self.builder.get_object("custAccBank1Entry").get_text()
        custAccName2 = self.builder.get_object("custAccName2Entry").get_text()
        custAccNo2 = self.builder.get_object("custAccNo2Entry").get_text()
        custAccBank2 = self.builder.get_object("custAccBank2Entry").get_text()

        msg = ""
        if custCode == "":
            msg += _("Customer code should not be empty.\n")
        else:
            codeQuery = share.config.db.session.query(
                Customers).select_from(Customers)
            codeQuery = codeQuery.filter(Customers.custCode == custCode)
            if self.editCustomer:
                codeQuery = codeQuery.filter(
                    Customers.custId != self.customerId)

            codeQuery = codeQuery.first()
            if codeQuery:
                msg += _("Customer code has been used before.\n")

        # --------------------
        groupid = 0
        if custGrp == "":
            msg += _("Customer group should not be empty.\n")
        else:
            query = share.config.db.session.query(CustGroups.custGrpId).select_from(
                CustGroups).filter(CustGroups.custGrpCode == custGrp)
            groupid = query.first()
            if groupid == None:
                msg += _("No customer group registered with code %s.\n") % utility.readNumber(custGrp)
            else:
                groupid = groupid[0]

        # --------------------
        if custName == "":
            msg += _("Customer name should not be empty.\n")

        # --------------------
        if msg != "":
            msgbox = Gtk.MessageDialog(
                self.customerForm, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, msg)
            msgbox.set_title(_("Can not save customer"))
            msgbox.run()
            msgbox.destroy()
            return -1

        if not self.editCustomer:
            # New Customer
            sub = class_subject.Subjects()
            custSubj = sub.add(dbconf.get_int('custSubject'), custName)
            customer = Customers(custCode, custName, custSubj, custPhone, custCell, custFax, custAddress,
                                 custEmail, custEcnmcsCode, custWebPage, callResponsible, custConnector,
                                 groupid, custPostalCode, custPersonalCode, custDesc,
                                 custRepViaEmail, custAccName1, custAccNo1, custAccBank1, custAccName2, custAccNo2,
                                 custAccBank2, custTypeBuyer, custTypeSeller, custTypeMate, custTypeAgent,
                                 custIntroducer, custCommission, custMarked, custReason, custDiscRate)
            share.config.db.session.add(customer)
        else:
            query = share.config.db.session.query(Customers).select_from(Customers)
            customer = query.filter(
                Customers.custId == self.customerId).first()
            # customer code not need to change
            #customer.custCode = custCode
            customer.custName = custName
            customer.custPhone = custPhone
            customer.custCell = custCell
            customer.custFax = custFax
            customer.custAddress = custAddress
            customer.custPostalCode = custPostalCode
            customer.custEmail = custEmail
            customer.custEcnmcsCode = custEcnmcsCode
            customer.custPersonalCode = custPersonalCode
            customer.custWebPage = custWebPage
            customer.custResponsible = callResponsible
            customer.custConnector = custConnector
            customer.custGroup = groupid
            customer.custDesc = custDesc
            # ----------------------------------
            customer.custTypeBuyer = custTypeBuyer
            customer.custTypeSeller = custTypeSeller
            customer.custTypeMate = custTypeMate
            customer.custTypeAgent = custTypeAgent
            customer.custIntroducer = custIntroducer
            customer.custCommission = custCommission
            customer.custDiscRate = custDiscRate
            customer.custMarked = custMarked
            customer.custReason = custReason
            # ----------------------------------
            customer.custAccName1 = custAccName1
            customer.custAccNo1 = custAccNo1
            customer.custAccBank1 = custAccBank1
            customer.custAccName2 = custAccName2
            customer.custAccNo2 = custAccNo2
            customer.custAccBank2 = custAccBank2

        share.config.db.session.commit()

        # Show new customer in table
        if self.treestore != None:
            parent_iter = self.treestore.get_iter_first()
            while parent_iter:
                itercode = self.treestore.get_value(parent_iter, 0)
                if itercode == utility.readNumber(custGrp):
                    break
                parent_iter = self.treestore.iter_next(parent_iter)
            custCode = utility.LN(custCode)

            if not self.editCustomer:
                self.treestore.append(parent_iter, (custCode, custName, utility.readNumber(
                    "0"), utility.readNumber("0"), utility.readNumber("0")))
            else:
                self.treestore.set(self.editIter, 0, custCode, 1, custName)

        return 0

    def editCustAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]

        if self.treestore.iter_parent(iter) == None:
            # Iter points to a customer group
            self.editCustomerGroup(sender)
        else:
            code = self.treestore.get_value(iter, 0)
            code = utility.convertToLatin(code)
            query = share.config.db.session.query(Customers, CustGroups.custGrpCode)
            query = query.select_from(
                outerjoin(CustGroups, Customers, CustGroups.custGrpId == Customers.custGroup))
            result = query.filter(Customers.custCode == code).first()
            customer = result[0]
            groupcode = result[1]

            custCode = utility. LN(customer.custCode, False)
            custGrp = utility. LN(groupcode, False)
            custPhone = utility. LN(customer.custPhone, False)
            custCell = utility. LN(customer.custCell, False)
            custFax = utility.LN(customer.custFax, False)
            custPostalCode = utility. LN(customer.custPostalCode, False)

            self.customerForm = self.builder.get_object("customersWindow")
            self.customerForm.set_title(_("Edit Customer"))
            self.builder.get_object(
                "addCustSubmitBtn").set_label(_("Save Customer"))

            self.builder.get_object("custCodeEntry").set_text(custCode)
            self.builder.get_object(
                "custNameEntry").set_text(customer.custName)
            self.custgrpentry.set_text(groupcode)
            self.builder.get_object("custEcnmcsCodeEntry").set_text(
                customer.custEcnmcsCode)
            self.builder.get_object("custPrsnalCodeEntry").set_text(
                customer.custPersonalCode)
            self.builder.get_object("custPhoneEntry").set_text(custPhone)
            self.builder.get_object("custCellEntry").set_text(custCell)
            self.builder.get_object("custFaxEntry").set_text(custFax)
            self.builder.get_object("custWebPageEntry").set_text(
                customer.custWebPage)
            self.builder.get_object(
                "custEmailEntry").set_text(customer.custEmail)
            self.builder.get_object("custRepViaEmailChk").set_active(
                customer.custRepViaEmail)
            self.builder.get_object("custAddressEntry").set_text(
                customer.custAddress)
            self.builder.get_object("callResponsibleEntry").set_text(
                customer.custResposible)
            self.builder.get_object("custConnectorEntry").set_text(
                customer.custConnector)
            self.builder.get_object(
                "custDescEntry").set_text(customer.custDesc)
            self.builder.get_object("custTypeBuyerChk").set_active(
                customer.custTypeBuyer)
            # ----------------------------------
            self.builder.get_object("custTypeSellerChk").set_active(
                customer.custTypeSeller)
            self.builder.get_object("custTypeMateChk").set_active(
                customer.custTypeMate)
            self.builder.get_object("custTypeAgentChk").set_active(
                customer.custTypeAgent)
            # self.custIntroducerEntry.set_text(customer.custIntroducer)
            self.boxCommissionRateEntry.set_text(customer.custCommission)
            self.boxDiscRateEntry.set_text(customer.custDiscRate)
            self.builder.get_object(
                "markedChk").set_active(customer.custMarked)
            self.builder.get_object(
                "markedReasonEntry").set_text(customer.custReason)
            # ----------------------------------aaaaaaaaaaaaaa
            self.builder.get_object("custAccName1Entry").set_text(
                customer.custAccName1)
            self.builder.get_object(
                "custAccNo1Entry").set_text(customer.custAccNo1)
            self.builder.get_object("custAccBank1Entry").set_text(
                customer.custAccBank1)
            self.builder.get_object("custAccName2Entry").set_text(
                customer.custAccName2)
            self.builder.get_object(
                "custAccNo2Entry").set_text(customer.custAccNo2)
            self.builder.get_object("custAccBank2Entry").set_text(
                customer.custAccBank2)

            self.builder.get_object("cusPostalCodeEntry").set_text(
                utility.LN(customer.custPostalCode, False))
            self.builder.get_object("markedReasonEntry").set_sensitive(
                self.builder.get_object("markedChk").get_active())

            self.customerForm.show_all()

            self.editCustomer = True
            self.customerId = customer.custId
            self.editIter = iter

    def deleteCustAndGrps(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        if iter != None:
            msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                                       Gtk.ButtonsType.OK_CANCEL, _("Are you sure to remove this row?"))
            msgbox.set_title(_("Are you sure?"))
            result = msgbox.run()
            msgbox.destroy()
            if result != Gtk.ResponseType.OK:
                return
        if self.treestore.iter_parent(iter) == None:
            # Iter points to a customer group
            self.deleteCustomerGroup(sender)
        else:
            # Iter points to a customer
            code = utility.convertToLatin(self.treestore.get_value(iter, 0))
            query = share.config.db.session.query(Customers)
            customer = query.filter(Customers.custCode == code).first()

            custId = customer.custId
            q1 = share.config.db.session.query(Factors.Cust).filter(
                Factors.Cust == custId)  # .limit(1)
            q2 = share.config.db.session.query(Cheque.chqCust).filter(
                Cheque.chqCust == custId)  # .limit(1)
            existsFlag = (q1.union(q2)).first()
            if existsFlag:
                msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
                                           _("Customer can not be deleted, Because there are some Factors or Cheques related to it. \nPlease delete them first.\n(Note: If there is some cheque, deleting that will not be usefull.)"))
                msgbox.set_title(_("Error deleting customer"))
                msgbox.run()
                msgbox.destroy()
            else:
                subjectCode = share.config.db.session.query(Subject).filter(
                    Subject.id == dbconf.get_int('custSubject')).first().code
                subjectCode = str(subjectCode) + str(code)
                # TODO check if this customer is used somewhere else

                share.config.db.session.delete(customer)
                share.config.db.session.delete(share.config.db.session.query(
                    Subject).filter(Subject.code == subjectCode).first())
                share.config.db.session.commit()
                self.treestore.remove(iter)

    # @param treeiter: the TreeIter which data should be saved in
    # @param data: a tuple containing data to be saved

    def saveRow(self, treeiter, data):
        if len(data) == 3:
            # A customer group should be saved, just set code and name.
            self.treestore.set(treeiter, 0, data[0], 1, data[1])
        elif len(data) == 4:
            # A customer should be saved, set all given data.
            self.treestore.set(
                treeiter, 0, data[0], 1, data[1], 2, data[2], 3, data[3])

    def on_addCustomerBtn_clicked(self, sender):
        selection = self.treeview.get_selection()
        iter = selection.get_selected()[1]
        pcode = ""
        if iter != None and self.treestore.iter_parent(iter) == None:
            pcode = self.treestore.get_value(iter, 0)
        self.addNewCustomer(sender, pcode)

    def selectGroup(self, sender):
        obj = customergroup.Group()
        obj.connect("group-selected", self.groupSelected)
        obj.viewCustomerGroups()

        code = self.custgrpentry.get_text()
        obj.highlightGroup(code)

    def groupSelected(self, sender, id, code):
        self.custgrpentry.set_text(code)
        sender.window.destroy()

    def selectcustomer(self, sender):
        obj = Customer()
        obj.connect("customer-selected", self.customerSelected)
        obj.viewCustomers(True)

        code = self.custIntroducerEntry.get_int()
        obj.highlightCust(code)

    def customerSelected(self, sender, id, code):
        self.custIntroducerEntry.set_text(code)
        sender.window.destroy()

    def highlightCust(self, code):
        '''        iter = self.treestore.get_iter_first()
        pre = iter

        while iter:
            itercode = self.treestore.get_value(iter, 0)
            if  itercode < code:
                pre = iter
                iter = self.treestore.iter_next(iter)
            elif itercode == code:
                break
            else:
                iter = pre
                break

        if not iter:
            iter = pre

        if iter:
            path = self.treestore.get_path(iter)
            self.treeview.scroll_to_cell(path, None, False, 0, 0)
            self.treeview.set_cursor(path, None, False)
            self.treeview.grab_focus()'''

    # Called when a row of customer table get activated by mouse double-click or Enter key
    def selectCustomerFromList(self, treeview, path, view_column):
        iter = self.treestore.get_iter(path)
        if self.treestore.iter_parent(iter) != None:
            code = utility.convertToLatin(self.treestore.get_value(iter, 0))

            query = share.config.db.session.query(Customers).select_from(Customers)
            query = query.filter(Customers.custCode == code)
            customer_id = query.first().custId
            self.emit("customer-selected", customer_id, code)


GObject.type_register(Customer)
GObject.signal_new("customer-selected", Customer, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_INT, GObject.TYPE_STRING))

## @}
