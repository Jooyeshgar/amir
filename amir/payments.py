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
from helpers import get_builder

class Payments(gobject.GObject):
	
	def __init__(self):
		gobject.GObject.__init__(self)
		
		self.builder = get_builder("SellingForm")
		self.window = self.builder.get_object("showPymnts")
		self.totalAmount = 0
		
		self.dueDateEntry = dateentry.DateEntry()
		self.builder.get_object("pymntDueDateBox").add(self.dueDateEntry)
		self.dueDateEntry.show()
		
		self.writeDateEntry = dateentry.DateEntry()
		self.builder.get_object("pymntWritingDateBox").add(self.writeDateEntry)
		self.writeDateEntry.show()
		
		self.paysTreeView = self.builder.get_object("paymentsTreeView")
		self.paysListStore = gtk.TreeStore(str, str, str, str, str, str, str, str, str)
		self.paysListStore.clear()
		self.paysTreeView.set_model(self.paysListStore)
		
		payHeaders = (_("No."), _("Paid by"), _("Amount"), _("Writing date"), _("Due Date"), 
					  _("Bank"), _("Serial No."), _("Track Code"), _("Description"))
		txt = 0
		for header in payHeaders:
			column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.paysTreeView.append_column(column)
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
		self.payerEntry     = self.builder.get_object("payerEntry")
		self.pymntAmntEntry = self.builder.get_object("pymntAmntEntry")
		
		#self.pymntDueDateBox  = self.builder.get_object("pymntDueDateBox")
		#self.pymntDueDateEntry  = DateEntry()#dateentry.DateEntry()
		#self.pymntDueDateBox.add(self.pymntDueDateEntry)
		#self.pymntDueDateEntry.show()
		today   = date.today()
		self.dueDateEntry.showDateObject(today)
		
		#self.pymntWritingDateBox   = self.builder.get_object("pymntWritingDateBox")
		#self.writingDateEntry  = DateEntry()#dateentry.DateEntry()
		#self.pymntWritingDateBox.add(self.writingDateEntry)
		#self.writingDateEntry.show()
		
		self.pymntDescEntry = self.builder.get_object("pymntDescEntry")
		self.bankEntry  = self.builder.get_object("bankEntry")
		self.serialNoEntry  = self.builder.get_object("serialNoEntry")
		self.chqPayerLbl    = self.builder.get_object("chqPayerLbl")
		self.trackingCodeEntry  = self.builder.get_object("trackingCodeEntry")
		
		#self.payerEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.writingDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntDueDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.bankEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.serialNoEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntDescEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		
		self.btn    = self.builder.get_object("submitBtn")
		self.btn.set_label(btnVal)
		
		self.pymntStBar   = self.builder.get_object("paymentsStatusBar")
		self.pymntStBar.push(1,"")
		self.addPymntDlg.show_all()
		
		#self.payerEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntDueDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		#self.pymntDescEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)

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

	def submitPayment(self,sender=0):
		self.validatePayment(save=True)

	def validatePayment(self,sender=0,ev=0,save=False):
		errFlg  = False
		sttsMsg = ""
		
		dueDte  = self.pymntDueDateEntry.get_text()
		if dueDte == "":
			msg = "You must enter the due date for the non-cash payment"
			if not sttsMsg:
				sttsMsg = msg
			self.pymntDueDateEntry.set_tooltip_text(msg)
			errFlg  = True
		else:
	#            print self.pymntDueDateEntry.getDateObject()
			self.pymntDueDateEntry.set_tooltip_text("")

		bank    = self.bankEntry.get_text()
		if bank == "":
			msg = "You must enter the bank for the non-cash payment"
			if not sttsMsg:
				sttsMsg = msg
			self.bankEntry.set_tooltip_text(msg)
			errFlg  = True
		else:
			self.bankEntry.set_tooltip_text("")

		serialNo    = self.serialNoEntry.get_text()
		if serialNo == "":
			msg = "You must enter the serial number for the non-cash payment"
			if not sttsMsg:
				sttsMsg = msg
			self.serialNoEntry.set_tooltip_text(msg)
			errFlg  = True
		else:
			self.serialNoEntry.set_tooltip_text("")

		pymntAmnt   = self.pymntAmntEntry.get_text()
		if pymntAmnt == "":
			pymntAmnt = "0.0"
		try:
			payment = float(pymntAmnt)
			self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
			self.pymntAmntEntry.set_tooltip_text("")
			self.pymntStBar.push(1,"")
		except:
			self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
			msg = "Payment Amount is not valid"
			if not sttsMsg:
				sttsMsg = msg
			self.pymntAmntEntry.set_tooltip_text(msg)
			errFlg  = True

		payer   = self.payerEntry.get_text()
		query   = self.session.query(Subject).select_from(Subject)
		query   = query.filter(Subject.code==payer).first()
		if not query:
			msg = "The payer code you entered is not a valid subject code."
			if not sttsMsg:
				sttsMsg = msg
			self.payerEntry.set_tooltip_text(msg)
			self.chqPayerLbl.set_text("")
			errFlg  = True
		else:
			self.payerEntry.set_tooltip_text("")
			self.chqPayerLbl.set_text(query.name)

		wrtDate = self.writingDateEntry.get_text()
		if wrtDate == "":
			msg = "You must enter a writing date for the non-cash payment"
			if not sttsMsg:
				sttsMsg = msg
			self.writingDateEntry.set_tooltip_text(msg)
			errFlg  = True
		else:
			self.writingDateEntry.set_tooltip_text("")
		
		self.pymntStBar.push(1,sttsMsg)
		#payHeaders = ("No.","Paid by","Amount","Writing date","Due Date","Bank","Serial No.","Track Code","Description")
		#----values:
		if save == True:
			if errFlg:
				errorstr = _("Some of the values you entered are not correct.\nThe payment cannot be saved.")
				msgbox = gtk.MessageDialog( self.addPymntDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
											gtk.BUTTONS_OK, errorstr )
				msgbox.set_title(_("Invalid data"))
				msgbox.run()
				msgbox.destroy()
				return

		if save == True:
			pymntAmnt   = self.pymntAmntEntry.get_text()
			wrtDate = self.writingDateEntry.get_text()
			dueDte  = self.pymntDueDateEntry.get_text()
			bank    = self.bankEntry.get_text()
			serialNo    = self.serialNoEntry.get_text()
			payer   = self.payerEntry.get_text()
			query   = self.session.query(Subject).select_from(Subject).filter(Subject.code==payer).first()
			payerName   = str(query.name)
			pymntDesc   = self.pymntDescEntry.get_text()
			trackCode   = self.trackingCodeEntry.get_text()

			if not self.edtPymntFlg:
				No  = len(self.paysItersDict) + 1
				paysList    = (str(No),payerName,pymntAmnt,wrtDate,dueDte,bank,serialNo,trackCode,pymntDesc)
				iter    = self.paysListStore.append(None,paysList)
				self.paysItersDict[No]   = iter
				self.addNonCashTtl(float(pymntAmnt))
				self.cancelPayment()
			
			else:
				print "IS EDITING..."
				#This block will edit the non-cash payment in the lists

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
				

gobject.type_register(Payments)
gobject.signal_new("payments-changed", Payments, gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, (gobject.TYPE_INT,))
                   