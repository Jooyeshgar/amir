import sys
import os
from datetime import date

from gi.repository import GObject
import gi
from gi.repository import Gtk
from gi.repository import Gdk

from sqlalchemy.sql import and_ , or_ , desc
from sqlalchemy.orm.util import outerjoin

import numberentry
import decimalentry
import dateentry
import subjects
import utility
import bankaccountsui
import customers
import class_bankaccounts

from database import *
from share import share
from helpers import get_builder, comboInsertItems

import logging

config = share.config

class Payments(GObject.GObject):
	
	chequeStatus = ["" , _("Paid-Not passed"), _("Paid-Passed"), _("Recieved-Not passed"), _("Recieved-Passed"), _("Spent") , _("Returned to customer") , _("Returned from customer") , _("Bounced")]
	chequePayment=[]
	recieptPayment=[]	
	
	def __init__(self, transId=0, sellFlag = 1 , spendCheque = False):
		
		#temp for vackground
		self.bank_names_count = 0
		self.sellFlag = sellFlag		
		self.chequesList = []		
		self.lastChqID = 0		
		#self.background = Gtk.Fixed()
		#self.background.put(Gtk.Image.new_from_file(os.path.join(config.data_path, "media", "background.png")), 0, 0)     # not working !
		#self.background.show_all()

		GObject.GObject.__init__(self)
		
		self.session = config.db.session
		self.builder = get_builder("cheque")
		self.window = self.builder.get_object("showPymnts")
		
		self.addPymntDlg = self.builder.get_object("addPaymentDlg")
		#self.spendCheque = spendCheque
		if spendCheque : 		# if is from automatic accounting-> spend cheque
			self.builder.get_object("addpaymentBtn") . set_sensitive(False)
			self.builder.get_object("editPaymentBtn") . set_sensitive(False)			
			self.builder.get_object("selectPayBtn") . set_sensitive(True)
		if transId : 			# if is from adding/editing factors 
			self.builder.get_object("selectPayBtn") . set_sensitive(True)
		self.totalAmount = 0
		self.numrecpts = 0
		self.numcheqs = 0
		self.transId = transId				
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
		
		self.chequeStatusLbl = self.builder.get_object("chequeStatusLbl")			
        
		self.isCheque = self.builder.get_object("chequeRadioButton")
		self.isRecpt = self.builder.get_object("recieptRadioButton")
		self.pymntDescEntry = self.builder.get_object("pymntDescEntry")
		self.bankEntry = self.builder.get_object("bankEntry")	
		if not self.sellFlag:
			self.builder.get_object("chooseBankBtn").set_sensitive(False)
		
		# add for bankcombo 23/11/92
		
		self.bankaccounts_class = class_bankaccounts.BankAccountsClass()
	 	self.bankCombo = self.builder.get_object('bank_names_combo')
		model = Gtk.ListStore(str)
		self.bankCombo.set_model(model)

		cell = Gtk.CellRendererText()
		self.bankCombo.pack_start(cell, True)
		# self.bankCombo.add_attribute(cell, 'text', 0)
		

	
				
		self.serialNoEntry = self.builder.get_object("serialNoEntry")
		self.payerEntry = self.builder.get_object("payerNameEntry")
		self.customerNameLbl = self.builder.get_object("customerNameLbl")			
		
		
		self.cheqTreeView = self.builder.get_object("chequeTreeView")
		self.cheqListStore = Gtk.ListStore(str, str, str, str, str, str, str, str, str , str)
		self.cheqListStore.clear()
		self.cheqTreeView.set_model(self.cheqListStore)
				
		payByTo = _("Payid by") if sellFlag else _("Payid to")

		
		cheqHeaders = (_("ID") , _("No."), payByTo, _("Amount"), _("Writing date"), _("Due Date"), 
					  _("Bank"), _("Serial No."), _("Status"), _("Description"))
		txt = 0
		for header in cheqHeaders:
			column = Gtk.TreeViewColumn(header,Gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.cheqTreeView.append_column(column)
			txt += 1
			
		self.chqSltWindow = self.builder.get_object("selectCheque")
		self.freeChequesTreeview = self.builder.get_object("freeChequesTreeview")
		self.sltCheqListStore = Gtk.ListStore(str, str, str, str, str, str, str, str, str , str)
		self.sltCheqListStore.clear()
		self.freeChequesTreeview.set_model(self.sltCheqListStore)

		payByTo = "Customer"
		cheqHeaders = (_("ID"), _("No."), payByTo, _("Amount"), _("Writing date"), _("Due Date"), 
					  _("Bank"), _("Serial No."), _("Status"), _("Description"))
		txt = 0
		for header in cheqHeaders:
			column = Gtk.TreeViewColumn(header,Gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.freeChequesTreeview.append_column(column)
			txt += 1


		self.builder.connect_signals(self)
		#
	
	#NOTE: Don't call this in __init__(), Because at initialize time, "payments-changed"
	# signal hasn't connected to factor forms yet, So payment-sum can not be shown there
	# even after the tables being filled.
	def fillPaymentTables(self):			
		self.fillChequeTable()	
		
	def fillChequeTable(self):
		total = 0
		if self.transId != 0 :					#  from factors 				
			if  self.sellFlag:
				#spendedCheuqesList =self.session.execute("select cheque.* from cheque join chequehistory on cheque.chqId = chequehistory.ChequeId where TransId = 4 and Status <>5 ")

				query = self.session.query(Cheque).select_from(ChequeHistory).filter(Cheque.chqId == ChequeHistory.ChequeId)\
					.filter(Cheque.chqStatus==5).filter(ChequeHistory.TransId == self.transId).order_by(ChequeHistory.Id.desc()).distinct(Cheque.chqId)				
				spendedCheuqesList = query.all()						
				self.chequesList+=spendedCheuqesList				
			query = self.session.query(Cheque)			
			query = query.filter(Cheque.chqTransId== self.transId).filter(Cheque.chqDelete == False)		
			cheqlist = query.all()
			self.chequesList +=  cheqlist 
			for cheq in self.chequesList:
				self.numcheqs += 1
				total += cheq.chqAmount
				ID = utility.LN(cheq.chqId)
				order = utility.LN(self.numcheqs, False)
				ID = utility.LN(cheq.chqId)
				amount = utility.LN(cheq.chqAmount)
				wrtDate = dateentry.dateToString(cheq.chqWrtDate)
				dueDate = dateentry.dateToString(cheq.chqDueDate)
				status = self.chequeStatus[cheq.chqStatus]
				bank = self.bankaccounts_class.get_bank_name (cheq.chqAccount)				
				customer = self.session.query(Customers) .filter(Customers.custId == cheq.chqCust).first().custName
				self.cheqListStore.append((ID , order, customer, amount, wrtDate, dueDate, bank, 
				                         cheq.chqSerial, status, cheq.chqDesc))			
			self.addToTotalAmount(total)
		cheque = self.session.query(Cheque).order_by(desc(Cheque.chqId)).first()
		if cheque != None :			
			self. lastChqID = cheque.chqId		
	
	def showPayments(self):
		self.window.show_all()
	
	def hidePayments(self, sender=0, ev=0):
		self.window.hide()
		#Returns true to avoid destroying payments window
		return True

        
	def addPayment(self, sender=0, is_cheque=True):					
		self.editingPay = None
		self.addPymntDlg.set_title(_("Add Non-Cash Payment"))
		self.edtPymntFlg = False
		self.removeFlg=False
		btnVal  = _("Add payment to list")
		
		model = self.bankCombo.get_model()
		if self.sellFlag: # other's cheque
			banks = self.bankaccounts_class.get_bank_names()
		else:
			banks =  self.bankaccounts_class.get_all_accounts()
		for item in banks:
			iter = model.append()
			name = item.Name if self.sellFlag else item.accName
			model.set(iter, 0, name )			

		today   = date.today()
		self.dueDateEntry.showDateObject(today)
		self.bankCombo.set_active(0)
		self.serialNoEntry.set_text("")
		self.pymntAmntEntry.set_text("")
		self.payerEntry.set_text("")		
		self.writeDateEntry.showDateObject(today)
		self.pymntDescEntry.set_text("")				

		self.btn    = self.builder.get_object("submitBtn")
		self.btn.set_label(btnVal)
		
		status = 3  if  self.sellFlag else 1 	# buy -> pardakhti , sell -> daryafti	
		self.chequeStatusLbl .set_text( self.chequeStatus[status])
		self.builder.get_object("paymentsStatusBar").push(1,"")
		self.addPymntDlg.show_all()



	def editPay(self, sender=0):
		model = self.bankCombo.get_model()
		if self.sellFlag: # other's cheque
			banks = self.bankaccounts_class.get_bank_names()
		else:
			banks =  self.bankaccounts_class.get_all_accounts()
		for item in banks:
			iter = model.append()
			name = item.Name if self.sellFlag else item.accName
			model.set(iter, 0, name )	

		iter = self.cheqTreeView.get_selection().get_selected()[1]
		if iter == None:
			return
		else:
			number = utility.convertToLatin(self.cheqListStore.get(iter, 1)[0])		
			number = utility.getInt(number)						
			cheque = self.chequesList [number-1]		# reads from cheques list that holds temporary changes in cheque table. for adding or edditing without effect on database before submiting factor form				
			self.editid = cheque.chqId
			#payer_id   = cheque.chqCust
			amount = utility.LN(cheque.chqAmount, False)
			serial = cheque.chqSerial
			wrtDate = cheque.chqWrtDate
			dueDate = cheque.chqDueDate
			desc = cheque.chqDesc
			
			self.chequeStatusLbl .set_text( self.chequeStatus[cheque.chqStatus])
			self.bankCombo.set_active(cheque.chqAccount - 1)
						
		self.edtPymntFlg = True
		self.edititer = iter		
		self.addPymntDlg.set_title(_("Edit Non-Cash Payment"))
		self.builder.get_object("submitBtn").set_label(_("Save Changes..."))
		self.builder.get_object("paymentsStatusBar").push(1,"")
		
		self.pymntAmntEntry.set_text(amount)
		self.serialNoEntry.set_text(serial)
		self.writeDateEntry.showDateObject(wrtDate)
		self.dueDateEntry.showDateObject(dueDate)
		self.pymntDescEntry.set_text(desc)		
		
		self.addPymntDlg.show_all()

	def removePay(self, sender):
		iter = self.cheqTreeView.get_selection().get_selected()[1]
		if iter == None:
			return
		
		number = utility.getInt(self.cheqListStore.get(iter, 1)[0])			
		msg = _("Are you sure to delete the cheque number %d?") % number
		msgBox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
		                           Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, msg)
		msgBox.set_title(_("Confirm Deletion"))
		answer = msgBox.run()
		msgBox.destroy()
		if answer != Gtk.ResponseType.OK:
			return
		ID = utility.getInt(self.cheqListStore.get(iter, 0)[0])			 
		cheque =self.session.query(Cheque). filter(Cheque.chqId == ID).first()
		self.removeCheque	(cheque)

		self.numcheqs -= 1
		liststore = self.cheqListStore
		del self.chequesList[number - 1]

		amount = utility.getInt(self.cheqListStore.get(iter, 3)[0])
		#self.session.commit()
		self.addToTotalAmount(-(amount))	
		hasrow = liststore.remove(iter)
		# if there is a row after the deleted one
		if hasrow:
			# Decrease the order-number in next rows
			while iter != None:
				number_str = utility.LN(number, False)
				liststore.set_value (iter, 1, number_str)
				number += 1
				iter = liststore.iter_next(iter)


	def submitPayment(self, sender=0):		
		if self.validatePayment() == False:
			return	
		pre_amnt 	= 0
		pymntAmnt 	= self.pymntAmntEntry.get_float()
		wrtDate 	= self.writeDateEntry.getDateObject()
		dueDte 		= self.dueDateEntry.getDateObject()
		bank = int(self.bankCombo.get_active()) + 1
		if self.sellFlag:
			bank_name = self.bankaccounts_class.get_bank_name(bank)		
		else:
			bank_name = self.bankaccounts_class.get_account(bank).accName
		serial 		= unicode(self.serialNoEntry.get_text())
		pymntDesc 	= unicode(self.pymntDescEntry.get_text())		
		payer		= self.payerEntry.get_text()		
		iter = None		
		pymnt_str = utility.LN(pymntAmnt)
		wrtDate_str = dateentry.dateToString(wrtDate)
		dueDte_str = dateentry.dateToString(dueDte)
		
		status = 3  if  self.sellFlag else 1 	# buy -> pardakhti , sell -> daryafti	
		if self.edtPymntFlg:
			iter = self.edititer
			number = utility.convertToLatin(self.cheqListStore.get(iter, 1)[0])
			number = utility.getInt(number)	
			cheque = self.chequesList[number - 1]
			if cheque.chqStatus == 5 :
				return
			query = self.session.query(Cheque)
			cheque = query.filter(and_(Cheque.chqTransId == cheque.chqTransId) ).first()
			pre_amnt = cheque.chqAmount
			cheque.chqAmount = pymntAmnt
			cheque.chqWrtDate = wrtDate
			cheque.chqDueDate = dueDte
			cheque.chqSerial = serial
			#cheque.chqStatus = status 			 must edit from automatic accounting
			cheque.chqCust = None  #self.payerEntry.get_text()		
			cheque.chqAccount = bank					
		#	cheque.chqOwnerName	= self.payerEntry.get_text()
			cheque.chqDesc = pymntDesc
			
			self.cheqListStore.set(iter, 2,self.customerNameLbl.get_text() , 3, pymnt_str,
			                      4, wrtDate_str, 5, dueDte_str, 6 ,unicode(bank_name) , 7, serial, 8, 
			                      self.chequeStatus[status], 9, pymntDesc)
			self. lastChqID += 1	

			self.chequesList[number-1] = Cheque(						
						pymntAmnt						,
						wrtDate							, 
						dueDte							, 
						serial							, 
						status							,			
						None							, 
			            bank							,
			            self.transId					, 
			            0					, #notebook ID 
			            pymntDesc						, 
			            0					,	#TODO must be a valid cheque history ID
			            0					,	#bill Id
			            number  			,	#order
			            chqId = cheque.chqId			)	
		else:		# adding cheque
			self.numcheqs += 1
			order = utility.LN(self.numcheqs)
			self. lastChqID += 1				
			cheque = Cheque(						
						pymntAmnt						,
						wrtDate							, 
						dueDte							, 
						serial							, 
						status							,
						None							, # customer Id . later after submiting factor or auto accounting will be updated 
			            bank							,
			            self.transId					, 
			            0						,
			            pymntDesc						, 
			            0					,
			            0					,
			           	order				,
			           	chqId = self.lastChqID	)				            				
			
			self.session.add(cheque)
			iter = self.cheqListStore.append((unicode(self.lastChqID ) , order ,self.customerNameLbl.get_text()  , pymnt_str, wrtDate_str, 
	                      dueDte_str, unicode(bank_name), serial, self.chequeStatus[status], pymntDesc))
			self.chequesList .append(cheque)								
			
			path = self.cheqListStore.get_path(iter)
			self.cheqTreeView.scroll_to_cell(path, None, False, 0, 0)
			self.cheqTreeView.set_cursor(path, None, False)

		#self.session.commit()
		self.addToTotalAmount(pymntAmnt - pre_amnt) # current pay value - prev pay value 
		self.addPymntDlg.hide()



	def validatePayment(self):
		
		errFlg  = False
		msg = ""
		
		dueDte = self.dueDateEntry.get_text()
		if dueDte == "":
			msg += _("You must enter the due date for the non-cash payment.\n")
			errFlg  = True
		
		payment = self.pymntAmntEntry.get_text()	
		if payment =="":
			 msg+=_("You must enter the Amount cheaue or reciep")
			 errFlg =True
		
	
		wrtDate = self.writeDateEntry.get_text()
		if wrtDate == "":
			msg = _("You must enter a writing date for the cheque.\n")
			errFlg  = True
			
		serialNo = self.serialNoEntry.get_text()
		if serialNo == "":
			msg += _("You must enter the serial number for the non-cash payment.\n")
			errFlg  = True			
				
		#----values:
		if errFlg:
			msg = _("The payment cannot be saved.\n\n%s") % msg
			msgbox = Gtk.MessageDialog( self.addPymntDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, msg )
			msgbox.set_title(_("Invalid data"))
			msgbox.run()
			msgbox.destroy()
			return False
		else:
			return True			

	def cancelPayment(self, sender=0, ev=0): 
		self.addPymntDlg.hide()		
		return True

	def addToTotalAmount(self, amount):
		self.totalAmount += amount
		ttlNonCashLabel = self.builder.get_object("ttlNonCashLabel")		
		total_str  = utility.LN(self.totalAmount)
		ttlNonCashLabel.set_text(total_str)
		self.emit("payments-changed", total_str)
	
	def chequeTreeView_button_press(self, sender, event):
		if event.type == Gdk.EventType._2BUTTON_PRESS:
			selection = self.cheqTreeView.get_selection()
			iter = selection.get_selected()[1]
			if iter != None :
				self.editPay(sender)
			else:
				self.addPayment(sender, True)

	def on_add_bank_clicked(self, sender):
		model = self.bankCombo.get_model()
		self.bankaccounts_class.addNewBank(model)

	def selectSeller(self,sender=0):				# not needed in submiting factor
		customer_win = customers.Customer()
		customer_win.viewCustomers()
		
	
		code = self.payerEntry.get_text()
		if code != '':
			customer_win.highlightCust(code)
		customer_win.connect("customer-selected",self.sellerSelected)

	def sellerSelected(self, sender, id, code):  	 # not needed in submiting factor
		self.payerEntry.set_text(code)
		sender.window.destroy()
		
		query = self.session.query(Customers).select_from(Customers)
		customer = query.filter(Customers.custId == id).first()
		
		self.payerEntry.set_text(customer.custId)	
				

	def selectPayBtn_clicked(self , sender):	
		self.sltCheqListStore.clear()	
		query = self.session.query(Cheque) . filter (or_(Cheque.chqStatus== 3, Cheque.chqStatus== 6 ) ).filter(Cheque.chqDelete == False)
		cheqlist = query.all()
		numcheqs = 0 
		for cheq in cheqlist:	
			numcheqs +=1					
			order = utility.LN(numcheqs, False)
			ID = utility.LN(cheq.chqId)
			amount = utility.LN(cheq.chqAmount)
			wrtDate = dateentry.dateToString(cheq.chqWrtDate)
			dueDate = dateentry.dateToString(cheq.chqDueDate)
			status = self.chequeStatus[cheq.chqStatus]
			bank = self.bankaccounts_class.get_bank_name (cheq.chqAccount)				
			customer = self.session.query(Customers) .filter(Customers.custId == cheq.chqCust).first()
			if customer != None:
				customer = customer.custName
			else: 
				continue
			self.sltCheqListStore.append((ID , order, customer, amount, wrtDate, dueDate, bank, 
			                         cheq.chqSerial, status, cheq.chqDesc	))
		self.chqSltWindow.show_all()

	def removeCheque(self,cheque) : 
		if cheque.chqStatus!= 5 : #cheque is just related to this transaction and is not spended from anywhere		
			if cheque.chqId == self.lastChqID:
				self.lastChqID -= 1		
			wasSubmited = self.session.query(Notebook).filter(cheque.chqId== Notebook.chqId).delete()			
			ch = cheque
			if wasSubmited :
				ch_history = ChequeHistory(ch.chqId, ch.chqAmount, ch.chqWrtDate, ch.chqDueDate, ch.chqSerial, ch.chqStatus, ch.chqCust, ch.chqAccount, ch.chqTransId, "deleted", date.today(),True)            
				
			#self.session.delete(cheque)
			cheque.chqDelete = True 
		else:		# is a spended cheque
			history = self.session.query(ChequeHistory).\
				filter(ChequeHistory.ChequeId == cheque.chqId).\
				filter(ChequeHistory.TransId != self.transId).\
				order_by(ChequeHistory.Id.desc()).limit(1).first()	

			dNotes = self.session.query(Notebook).filter(cheque.chqId== Notebook.chqId).order_by(Notebook.id.desc()).limit(2).all()
			if len(dNotes):
				self.session.query(Notebook).filter(or_(Notebook.id==dNotes[0].id ,Notebook.id== dNotes[1].id  )).delete()

			#revert cheque to  it's last history of previous Factor before the cheque spended 
			cheque.chqAmount = history.Amount
			cheque.chqWrtDate = history.WrtDate 
			cheque.chqDueDate = history.DueDate
			cheque.chqSerial  = history.Serial
			cheque . chqStatus = history. Status 
			cheque. chqCust  = history.Cust
			cheque.chqAccount = history.Account
			cheque.chqTransId  = history.TransId
			cheque.chqDesc = history.Desc
			ch = cheque
			ch_history = ChequeHistory(ch.chqId, ch.chqAmount, ch.chqWrtDate, ch.chqDueDate, ch.chqSerial, ch.chqStatus, ch.chqCust, ch.chqAccount, ch.chqTransId, "Unspended", date.today(),True)            
		self.session.add(ch_history)
		self.session.commit()


	def closeSltChqWnd (self , sender= None , ser_data = None):
		self. chqSltWindow . hide()
		return True
		
	def onFreeChequeSelected (self , sender , path = None , col = 0):		
		treeiter = self.sltCheqListStore.get_iter(path)
		chequeId = self.sltCheqListStore.get_value(treeiter , 0)
		cheque = self.session.query(Cheque ) . filter(Cheque.chqId == chequeId).first()		
		cheque.chqStatus = 5		
		cheque.chqTransId = self.transId 
		self.chequesList .append(cheque)
		self.numcheqs  += 1 
		#chequeNo = self.sltCheqListStore.get_value(treeiter , 1)
		chequeCust = self.sltCheqListStore.get_value(treeiter , 2)			
		chequeAmnt = self.sltCheqListStore.get_value(treeiter , 3)
		chequeWDate = self.sltCheqListStore.get_value(treeiter , 4)
		chequeDDate = self.sltCheqListStore.get_value(treeiter , 5)
		chequeBank = self.sltCheqListStore.get_value(treeiter , 6)
		chequeSerial = self.sltCheqListStore.get_value(treeiter , 7)
		chequeStatus = self.chequeStatus[cheque.chqStatus] #self.sltCheqListStore.get_value(treeiter , 7)
		chequeDesc = self.sltCheqListStore.get_value(treeiter , 7)
		self.cheqListStore.append((chequeId , utility.LN(self.numcheqs  ),chequeCust  , chequeAmnt, chequeWDate, 
	           chequeDDate, chequeBank, chequeSerial, chequeStatus, chequeDesc))

		self.addToTotalAmount(utility.getFloat(chequeAmnt) ) 
		#self.cheqListStore .append(cheque)
		self.closeSltChqWnd()


GObject.type_register(Payments)
GObject.signal_new("payments-changed", Payments, GObject.SignalFlags.RUN_LAST,
                   None, (GObject.TYPE_STRING,))
                   