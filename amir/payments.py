import sys
import os
from datetime import date

import gobject
import pygtk
import gtk

from sqlalchemy.sql import and_
from sqlalchemy.orm.util import outerjoin

import numberentry
import decimalentry
import dateentry
import subjects
import utility

from database import *
from amirconfig import config
from helpers import get_builder, comboInsertItems

class Payments(gobject.GObject):
	
	chequeStatus = [_("Pending"), _("In Account"), _("Refused"), _("Paid"), _("Spent")]
	
	def __init__(self, transId=0, billId=0):
		gobject.GObject.__init__(self)
		
		self.session = config.db.session
		self.builder = get_builder("SellingForm")
		self.window = self.builder.get_object("showPymnts")
		
		self.totalAmount = 0
		self.numrecpts = 0
		self.numcheqs = 0
		self.transId = transId
		self.billId = billId
		self.payer = None
		
		self.pymntAmntEntry = decimalentry.DecimalEntry()
		self.builder.get_object("pymntAmntBox").add(self.pymntAmntEntry)
		self.pymntAmntEntry.show()
		
		self.dueDateEntry = dateentry.DateEntry()
		self.builder.get_object("pymntDueDateBox").add(self.dueDateEntry)
		self.dueDateEntry.show()
		
		self.writeDateEntry = dateentry.DateEntry()
		self.builder.get_object("pymntWritingDateBox").add(self.writeDateEntry)
		self.writeDateEntry.show()
		
		self.cheqStatusList = self.builder.get_object("cheqStatusComboBox")
		comboInsertItems(self.cheqStatusList, self.chequeStatus)
		self.cheqStatusList.set_active(0)
        
		self.isCheque = self.builder.get_object("chequeRadioButton")
		self.isRecpt = self.builder.get_object("recieptRadioButton")
		self.pymntDescEntry = self.builder.get_object("pymntDescEntry")
		self.bankEntry = self.builder.get_object("bankEntry")
		self.serialNoEntry = self.builder.get_object("serialNoEntry")
		self.payerEntry = self.builder.get_object("payerCodeEntry")
		self.trackingCodeEntry = self.builder.get_object("trackingCodeEntry")
		self.bankAccountEntry = self.builder.get_object("bankAccountEntry")
		
		self.paysTreeView = self.builder.get_object("receiptTreeView")
		self.paysListStore = gtk.ListStore(str, str, str, str, str, str, str, str, str)
		self.paysListStore.clear()
		self.paysTreeView.set_model(self.paysListStore)
		
		self.cheqTreeView = self.builder.get_object("chequeTreeView")
		self.cheqListStore = gtk.ListStore(str, str, str, str, str, str, str, str, str)
		self.cheqListStore.clear()
		self.cheqTreeView.set_model(self.cheqListStore)
		
		payHeaders = (_("No."), _("Paid by"), _("Amount"), _("Writing date"), _("Due Date"), 
					  _("Bank"), _("Serial No."), _("Track Code"), _("Description"))
		txt = 0
		for header in payHeaders:
			column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.paysTreeView.append_column(column)
			txt += 1
		
		cheqHeaders = (_("No."), _("Paid by"), _("Amount"), _("Writing date"), _("Due Date"), 
					  _("Bank"), _("Serial No."), _("Status"), _("Description"))
		txt = 0
		for header in cheqHeaders:
			column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.cheqTreeView.append_column(column)
			txt += 1
			
		self.builder.connect_signals(self)
	
	#NOTE: Don't call this in __init__(), Because at initialize time, "payments-changed"
	# signal hasn't connected to factor forms yet, So payment-sum can not be shown there
	# even after the tables being filled.
	def fillPaymentTables(self):
		self.fillRecptTable()
		self.fillChequeTable()
	
	def fillRecptTable(self):
		total = 0
		query = self.session.query(Payment, Customers.custName)
		query = query.select_from(outerjoin(Payment, Customers, Payment.paymntPayer == Customers.custId))
		query = query.filter(and_(Payment.paymntTransId == self.transId, 
		                          Payment.paymntBillId == self.billId))
		paylist = query.order_by(Payment.paymntOrder.asc()).all()
		for pay, cname in paylist:
			self.numrecpts += 1
			total += pay.paymntAmount
			order = utility.showNumber(self.numrecpts, False)
			amount = utility.showNumber(pay.paymntAmount)
			wrtDate = dateentry.dateToString(pay.paymntWrtDate)
			dueDate = dateentry.dateToString(pay.paymntDueDate)
			
			self.paysListStore.append((order, cname, amount, wrtDate, dueDate, pay.paymntBank,
			                         pay.paymntSerial, pay.paymntTrckCode, pay.paymntDesc))
		self.addToTotalAmount(total)
		
	def fillChequeTable(self):
		total = 0
		query = self.session.query(Cheque, Customers.custName)
		query = query.select_from(outerjoin(Cheque, Customers, Cheque.chqCust == Customers.custId))
		query = query.filter(and_(Cheque.chqTransId == self.transId, 
		                          Cheque.chqBillId == self.billId))
		cheqlist = query.order_by(Cheque.chqOrder.asc()).all()
		for cheq, cname in cheqlist:
			self.numcheqs += 1
			total += cheq.chqAmount
			order = utility.showNumber(self.numcheqs, False)
			amount = utility.showNumber(cheq.chqAmount)
			wrtDate = dateentry.dateToString(cheq.chqWrtDate)
			dueDate = dateentry.dateToString(cheq.chqDueDate)
			status = self.chequeStatus[cheq.chqStatus]
			
			self.cheqListStore.append((order, cname, amount, wrtDate, dueDate, "", 
			                         cheq.chqSerial, status, cheq.chqDesc))
		self.addToTotalAmount(total)
	
	def showPayments(self):
		self.window.show_all()
	
	def hidePayments(self, sender=0, ev=0):
		self.window.hide_all()
		#Returns true to avoid destroying payments window
		return True
		
	#def setTotalAmount(self, value):
		#self.totalAmount = value
		#self.emit("payments-changed", value)
        
	def addPayment(self,sender=0,edit=None):
		self.addPymntDlg = self.builder.get_object("addPaymentDlg")
		
		self.editingPay = None
		self.addPymntDlg.set_title(_("Add Non-Cash Payment"))
		self.edtPymntFlg = False
		btnVal  = _("Add payment to list")
		
		self.pymntAmntEntry.set_text("")
		self.bankEntry.set_text("")
		self.serialNoEntry.set_text("")
		self.payerEntry.set_text("")
		self.builder.get_object("chqPayerLbl").set_text("")
		self.pymntDescEntry.set_text("")
		self.trackingCodeEntry.set_text("")
		self.cheqStatusList.set_active(0)
		self.bankAccountEntry.set_text("")
		
		today   = date.today()
		self.dueDateEntry.showDateObject(today)
		self.writeDateEntry.showDateObject(today)
			
		self.btn    = self.builder.get_object("submitBtn")
		self.btn.set_label(btnVal)
		
		self.isCheque.set_sensitive(True)
		self.isRecpt.set_sensitive(True)
		self.builder.get_object("paymentsStatusBar").push(1,"")
		self.addPymntDlg.show_all()


	def submitPayment(self, sender=0):
		if self.validatePayment() == False:
			return

		pre_amnt = 0
		pymntAmnt = self.pymntAmntEntry.get_float()
		wrtDate = self.writeDateEntry.getDateObject()
		dueDte = self.dueDateEntry.getDateObject()
		bank = unicode(self.bankEntry.get_text())
		serial = unicode(self.serialNoEntry.get_text())
		pymntDesc = unicode(self.pymntDescEntry.get_text())
		iter = None
		
		pymnt_str = utility.showNumber(pymntAmnt)
		wrtDate_str = dateentry.dateToString(wrtDate)
		dueDte_str = dateentry.dateToString(dueDte)
		
		if self.isCheque.get_active():
			status = self.cheqStatusList.get_active()
			if self.edtPymntFlg:
				query = self.session.query(Cheque).select_from(Cheque)
				cheque = query.filter(Cheque.chqId == self.editid).first()
				pre_amnt = cheque.chqAmount
				cheque.chqAmount = pymntAmnt
				cheque.chqWrtDate = wrtDate
				cheque.chqDueDate = dueDte
				cheque.chqSerial = serial
				cheque.chqStatus = status
				cheque.chqCust = self.payer.custId
				cheque.chqDesc = pymntDesc
				iter = self.edititer
				self.cheqListStore.set(self.edititer, 1, self.payer.custName, 2, pymnt_str,
				                      3, wrtDate_str, 4, dueDte_str, 6, serial, 7, 
				                      self.chequeStatus[status], 8, pymntDesc)
			else:
				self.numcheqs += 1
				order = utility.showNumber(self.numcheqs)
				cheque = Cheque(pymntAmnt, wrtDate, dueDte, serial, status, self.payer.custId,
				                self.transId, self.billId, pymntDesc, self.numcheqs)
				iter = self.cheqListStore.append((order, self.payer.custName, pymnt_str, wrtDate_str, 
		                      dueDte_str, bank, serial, self.chequeStatus[status], pymntDesc))
			
			self.session.add(cheque)
			self.session.commit()
			path = self.cheqListStore.get_path(iter)
			self.cheqTreeView.scroll_to_cell(path, None, False, 0, 0)
			self.cheqTreeView.set_cursor(path, None, False)
			
		else:
			trackCode = unicode(self.trackingCodeEntry.get_text())
			if self.edtPymntFlg:
				query = self.session.query(Payment).select_from(Payment)
				payment = query.filter(Payment.paymntId == self.editid).first()
				pre_amnt = payment.paymntAmount
				payment.paymntDueDate = dueDte
				payment.paymntBank = bank
				payment.paymntSerial = serial
				payment.paymntAmount = pymntAmnt
				payment.paymntPayer = self.payer.custId
				payment.paymntWrtDate = wrtDate
				payment.paymntDesc = pymntDesc
				payment.paymntTrckCode = trackCode
				iter = self.edititer
				self.paysListStore.set(self.edititer, 1, self.payer.custName, 2, pymnt_str,
				                      3, wrtDate_str, 4, dueDte_str, 5, bank, 6, serial,
				                      7, trackCode, 8, pymntDesc)
			else:
				self.numrecpts += 1
				order = utility.showNumber(self.numrecpts)
				payment = Payment(dueDte, bank, serial, pymntAmnt, self.payer.custId, wrtDate,
				                 pymntDesc, self.transId, self.billId, trackCode, self.numrecpts)
				iter = self.paysListStore.append((order, self.payer.custName, pymnt_str, wrtDate_str, 
		                      dueDte_str, bank, serial, trackCode, pymntDesc))
		                      
			self.session.add(payment)
			self.session.commit()
			path = self.paysListStore.get_path(iter)
			self.paysTreeView.scroll_to_cell(path, None, False, 0, 0)
			self.paysTreeView.set_cursor(path, None, False)
		
		self.addToTotalAmount(pymntAmnt - pre_amnt)
		self.addPymntDlg.hide()


	def validatePayment(self):
		errFlg  = False
		msg = ""
		
		dueDte = self.dueDateEntry.get_text()
		if dueDte == "":
			msg += _("You must enter the due date for the non-cash payment.\n")
			errFlg  = True
		
		payment = self.pymntAmntEntry.get_float()
		
		#payer_code = self.payerEntry.get_text()
		#query = self.session.query(Customers).select_from(Customers)
		#query = query.filter(Customers.custCode == payer_code).first()
		if not self.payer:
			msg = _("The payer code you entered is not a valid subject code.\n")
			errFlg  = True
			
		if self.isCheque.get_active():
			wrtDate = self.writeDateEntry.get_text()
			if wrtDate == "":
				msg = _("You must enter a writing date for the cheque.\n")
				errFlg  = True
				
			serialNo = self.serialNoEntry.get_text()
			if serialNo == "":
				msg += _("You must enter the serial number for the non-cash payment.\n")
				errFlg  = True
		else:
			bank = self.bankEntry.get_text()
			if bank == "":
				msg += _("You must enter the bank for the non-cash payment.\n")
				errFlg  = True
		
		#payHeaders = ("No.","Paid by","Amount","Writing date","Due Date","Bank","Serial No.","Track Code","Description")
		#----values:
		if errFlg:
			msg = _("The payment cannot be saved.\n\n%s") % msg
			msgbox = gtk.MessageDialog( self.addPymntDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
										gtk.BUTTONS_OK, msg )
			msgbox.set_title(_("Invalid data"))
			msgbox.run()
			msgbox.destroy()
			return False
		else:
			return True
			
	def validatePayer(self, sender=0, ev=0):
		payer_code = unicode(self.payerEntry.get_text())
		query = self.session.query(Customers).select_from(Customers)
		self.payer = query.filter(Customers.custCode == payer_code).first()
		
		if not self.payer:
			msg = _("The payer code you entered is not a valid subject code.")
			self.payerEntry.set_tooltip_text(msg)
			self.builder.get_object("chqPayerLbl").set_text("")
			self.builder.get_object("paymentsStatusBar").push(1,msg)
		else:
			self.payerEntry.set_tooltip_text("")
			self.builder.get_object("paymentsStatusBar").push(1,"")
			self.builder.get_object("chqPayerLbl").set_text(self.payer.custName)

		

	def editPay(self, sender=0):
		iter = self.paysTreeView.get_selection().get_selected()[1]
		if iter == None:
			iter = self.cheqTreeView.get_selection().get_selected()[1]
			if iter == None:
				return
			else:
				number = utility.convertToLatin(self.cheqListStore.get(iter, 0)[0])
				query = self.session.query(Cheque).select_from(Cheque)
				query = query.filter(and_(Cheque.chqTransId == self.transId, 
				                    Cheque.chqBillId == self.billId, Cheque.chqOrder == number))
				cheque = query.first()
				
				self.editid = cheque.chqId
				payer_id   = cheque.chqCust
				amount = utility.showNumber(cheque.chqAmount, False)
				serial = cheque.chqSerial
				wrtDate = cheque.chqWrtDate
				dueDate = cheque.chqDueDate
				desc = cheque.chqDesc
				
				self.isCheque.set_active(True)
				self.isCheque.set_sensitive(True)
				self.isRecpt.set_sensitive(False)
				self.cheqStatusList.set_active(cheque.chqStatus)
				self.trackingCodeEntry.set_text("")
				self.bankEntry.set_text("")
		else:
			number = utility.convertToLatin(self.paysListStore.get(iter, 0)[0])
			query = self.session.query(Payment).select_from(Payment)
			query = query.filter(and_(Payment.paymntTransId == self.transId, 
				                Payment.paymntBillId == self.billId, Payment.paymntOrder == number))
			payment = query.first()
			
			self.editid = payment.paymntId
			payer_id   = payment.paymntPayer
			amount = utility.showNumber(payment.paymntAmount, False)
			serial = payment.paymntSerial
			wrtDate = payment.paymntWrtDate
			dueDate = payment.paymntDueDate
			desc = payment.paymntDesc
			
			self.isRecpt.set_active(True)
			self.isRecpt.set_sensitive(True)
			self.isCheque.set_sensitive(False)
			self.trackingCodeEntry.set_text(payment.paymntTrckCode)
			self.bankEntry.set_text(payment.paymntBank)
		
		self.edtPymntFlg = True
		self.edititer = iter
		self.addPymntDlg = self.builder.get_object("addPaymentDlg")
		self.addPymntDlg.set_title(_("Edit Non-Cash Payment"))
		self.builder.get_object("submitBtn").set_label(_("Save Changes..."))
		self.builder.get_object("paymentsStatusBar").push(1,"")
		
		query = self.session.query(Customers).select_from(Customers)
		customer = query.filter(Customers.custId == payer_id).first()
		self.payerEntry.set_text(customer.custCode)
		self.builder.get_object("chqPayerLbl").set_text(customer.custName)
		
		self.pymntAmntEntry.set_text(amount)
		self.serialNoEntry.set_text(serial)
		self.writeDateEntry.showDateObject(wrtDate)
		self.dueDateEntry.showDateObject(dueDate)
		self.pymntDescEntry.set_text(desc)
		
		self.addPymntDlg.show_all()

	def removePay(self,sender):
		delIter = self.paysTreeView.get_selection().get_selected()[1]
		if delIter:
			No  = int(self.paysListStore.get(delIter, 0)[0])
			msg = _("Are You sure you want to delete the non-cash payment row number %s ?") %No
			msgBox  = gtk.MessageDialog( self.showPymnts, gtk.DIALOG_MODAL,
											gtk.MESSAGE_QUESTION,
											gtk.BUTTONS_OK_CANCEL, msg         )
			msgBox.set_title(            _("Confirm Deletion")              )
			answer  = msgBox.run(                                           )
			msgBox.destroy(                                                 )
			if answer != gtk.RESPONSE_OK:
				return
			nonCashAmnt = float(self.paysListStore.get(delIter,2)[0])
			self.remNonCashTtl(nonCashAmnt)
			self.paysListStore.remove(delIter)
			print "1-\tdef removePay()"
			if len(self.paysItersDict) > 1:
				print "2"
				while No < len(self.paysItersDict):
					print "3"
					nextIter    = self.paysItersDict[No+1]
					print "4"
					self.paysListStore.set_value(nextIter,0,str(No))
					print "5"
					self.paysItersDict[No] = nextIter
					print "6"
					del self.paysItersDict[No+1]
					print "7"
					No  += 1
					print "8"
			else:
				print "9"
				self.paysItersDict = {}
				print "10"

	def cancelPayment(self, sender=0, ev=0):
		self.addPymntDlg.hide_all()
		return True
		
	def upPayInList(self,sender):
		if len(self.paysItersDict) == 1:
			return
		iter    = self.paysTreeView.get_selection().get_selected()[1]
		if iter:
			No   = int(self.paysListStore.get(iter, 0)[0])
			abvNo   = No - 1
			if abvNo > 0:
				aboveIter   = self.paysItersDict[abvNo]
				self.paysListStore.move_before(iter,aboveIter)
				self.paysItersDict[abvNo]  = iter
				self.paysItersDict[No]     = aboveIter
				self.paysListStore.set_value(iter,0,str(abvNo))
				self.paysListStore.set_value(aboveIter,0,str(No))

	def downPayInList(self,sender):
		if len(self.paysItersDict) == 1:
			return
		iter    = self.paysTreeView.get_selection().get_selected()[1]
		if iter:
			No   = int(self.paysListStore.get(iter, 0)[0])
			blwNo   = No + 1
			if No < len(self.paysItersDict):
				belowIter   = self.paysItersDict[blwNo]
				self.paysListStore.move_after(iter,belowIter)
				self.paysItersDict[blwNo]  = iter
				self.paysItersDict[No]     = belowIter
				self.paysListStore.set_value(iter,0,str(blwNo))
				self.paysListStore.set_value(belowIter,0,str(No))
				

	def addToTotalAmount(self, amount):
		self.totalAmount += amount
		ttlNonCashLabel = self.builder.get_object("ttlNonCashLabel")
		#lastAmnt = utility.getFloatNumber(ttlNonCashLabel.get_text())
		total_str  = utility.showNumber(self.totalAmount)
		ttlNonCashLabel.set_text(total_str)
		print "sig called"
		self.emit("payments-changed", total_str)
		
	def activate_Cheque(self, sender=0):
		self.builder.get_object("chequeInfoBox").set_sensitive(True)
		self.builder.get_object("bankBox").set_sensitive(False)
		self.builder.get_object("trackingCodeEntry").set_sensitive(False)
	
	def activate_BankReciept(self, sender=0):
		self.builder.get_object("chequeInfoBox").set_sensitive(False)
		self.builder.get_object("bankBox").set_sensitive(True)
		self.builder.get_object("trackingCodeEntry").set_sensitive(True)
		
	def chequeListActivated(self, treeview):
		self.paysTreeView.get_selection().unselect_all()
		
	def paysListActivated(self, treeview):
		self.cheqTreeView.get_selection().unselect_all()
		
gobject.type_register(Payments)
gobject.signal_new("payments-changed", Payments, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
                   