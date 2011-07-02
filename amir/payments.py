import sys
import os
from datetime import date

import gobject
import pygtk
import gtk

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
		
	def showPayments(self):
		self.window.show_all()
		
	def setTotalAmount(self, value):
		self.totalAmount = value
		self.emit("payments-changed", value)
        
	def addPayment(self,sender=0,edit=None):
		self.addPymntDlg = self.builder.get_object("addPaymentDlg")
		if edit:
			self.editPymntNo    = edit[0]
			ttl = _("Edit Non-Cash Payment:\t%s - %s") %(self.editPymntNo,edit[1])
			self.addPymntDlg.set_title(ttl)
			self.edtPymntFlg = True
			btnVal  = _("Save Changes...")
		else:
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
		
		self.builder.get_object("paymentsStatusBar").push(1,"")
		self.addPymntDlg.show_all()
		
		

		if self.edtPymntFlg:
			#("No.","Paid by","Amount","Writing date","Due Date","Bank","Serial No.","Track Code","Description")
			(No,payer,amnt,wrtDate,dueDate,bank,serial,trckCd,desc) = edit
			payer   = unicode(payer)
			sub = self.session.query(Subject).select_from(Subject).filter(Subject.name==payer).first()
			self.payerEntry.set_text(sub.code)
			self.pymntAmntEntry.set_text(amnt)
	#            self.writingDateEntry.showDateObject(wrtDate)
	#            self.pymntDueDateEntry.showDateObject(dueDate)
			self.bankEntry.set_text(bank)
			self.serialNoEntry.set_text(serial)
			self.trackingCodeEntry.set_text(trckCd)
			self.pymntDescEntry.set_text(desc)

	def submitPayment(self, sender=0):
		if self.validatePayment() == False:
			return

		pymntAmnt = self.pymntAmntEntry.get_float()
		wrtDate = self.writeDateEntry.getDateObject()
		dueDte = self.dueDateEntry.getDateObject()
		bank = unicode(self.bankEntry.get_text())
		serial = unicode(self.serialNoEntry.get_text())
		pymntDesc = unicode(self.pymntDescEntry.get_text())
		
		pymnt_str = utility.showNumber(pymntAmnt)
		wrtDate_str = dateentry.dateToString(wrtDate)
		dueDte_str = dateentry.dateToString(dueDte)
		
		if self.isCheque.get_active():
			self.numcheqs += 1
			status = self.cheqStatusList.get_active() 
			cheque = Cheque(pymntAmnt, wrtDate, dueDte, serial, status, self.payer.custId,
			                self.transId, self.billId, pymntDesc, self.numcheqs)
			self.session.add(cheque)
			self.session.commit()
			
			self.cheqListStore.append((self.numcheqs, self.payer.custName, pymnt_str, wrtDate_str, 
		                      dueDte_str, bank, serial, self.chequeStatus[status], pymntDesc))
		else:
			self.numrecpts += 1
			trackCode = unicode(self.trackingCodeEntry.get_text())
			payment = Payment(dueDte, bank, serial, pymntAmnt, self.payer.custId, wrtDate,
			                  pymntDesc, self.transId, self.billId, trackCode, self.numrecpts)
			self.session.add(payment)
			self.session.commit()
			
			self.paysListStore.append((self.numrecpts, self.payer.custName, pymnt_str, wrtDate_str, 
		                      dueDte_str, bank, serial, trackCode, pymntDesc))
		
		self.addToTotalAmount(pymntAmnt)
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
			#errorstr = _("Some of the values you entered are not correct.\nThe payment cannot be saved.")
			msgbox = gtk.MessageDialog( self.addPymntDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
										gtk.BUTTONS_OK, msg )
			msgbox.set_title(_("Invalid data"))
			msgbox.run()
			msgbox.destroy()
			return False
		else:
			return True
			
	def validatePayer(self, sender=0, ev=0):
		payer_code = self.payerEntry.get_text()
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

		

	def editPay(self,sender=0):
		iter    = self.paysTreeView.get_selection().get_selected()[1]
		if iter != None :
			self.editingPay    = iter
			No      = self.paysListStore.get(iter, 0)[0]
			payer   = self.paysListStore.get(iter, 1)[0]
			amnt    = self.paysListStore.get(iter, 2)[0]
			wrtDate = self.paysListStore.get(iter, 3)[0]
			dueDate = self.paysListStore.get(iter, 4)[0]
			bank    = self.paysListStore.get(iter, 5)[0]
			serial  = self.paysListStore.get(iter, 6)[0]
			trckCd  = self.paysListStore.get(iter, 7)[0]
			desc    = self.paysListStore.get(iter, 8)[0]
			#payment = self.session.query(
			edtTpl  = (No,payer,amnt,wrtDate,dueDate,bank,serial,trckCd,desc)
			self.addPayment(edit=edtTpl)

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
		ttlNonCashLabel = self.builder.get_object("ttlNonCashLabel")
		lastAmnt = utility.getFloatNumber(ttlNonCashLabel.get_text())
		total  = lastAmnt + amount
		ttlNonCashLabel.set_text(utility.showNumber(total))
		self.emit("payments-changed", total)
		
	def activate_Cheque(self, sender):
		self.builder.get_object("chequeInfoBox").set_sensitive(True)
		self.builder.get_object("bankBox").set_sensitive(False)
		self.builder.get_object("trackingCodeEntry").set_sensitive(False)
	
	def activate_BankReciept(self, sender):
		self.builder.get_object("chequeInfoBox").set_sensitive(False)
		self.builder.get_object("bankBox").set_sensitive(True)
		self.builder.get_object("trackingCodeEntry").set_sensitive(True)
		
		
gobject.type_register(Payments)
gobject.signal_new("payments-changed", Payments, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_FLOAT,))
                   