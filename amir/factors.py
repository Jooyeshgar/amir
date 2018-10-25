# -*- coding: utf-8 -*-
import os

import  product
import  numberentry
import  decimalentry
from    dateentry       import  *
import  subjects
import  utility
import  payments
import  dbconfig
import  customers

from    sqlalchemy.orm              import  sessionmaker, join
from    helpers                     import  get_builder
from    sqlalchemy.orm.util         import  outerjoin
from    share                       import  share
from    datetime                    import  date
from    sqlalchemy.sql              import  and_
from    sqlalchemy.sql.functions    import  *
from    database                    import  *
import	class_document
import  class_cheque
from gi.repository import Gtk
from gi.repository import Gdk
from payments import Payments
from weasyprintreport import *
#import logging

config = share.config

## \defgroup Controller
## @{

class Factor(Payments):
	"""Manage sell and buy form."""

	def __init__(self,sell = True, transId=None):
		self.sell = sell 	#Sell or buy
		#self.addFalg = True
		self.editFlag = False   #  false means  adding
		self.editTransaction = None
		self.removeFlag = False
		self.listTotalDiscount = 0.0
		self.totalFactor = 0
		self.totalTax = 0
		self.VAT = 0
		self.fee = 0
		self.vatCheck = True

		self.session = config.db.session	
		self.Document = class_document.Document()
		
		query   = self.session.query(Factors.Id).select_from(Factors)
		lastId  = query.order_by(Factors.Id.desc()).first()			
		if not lastId:
			lastId  = 0
		else:
			lastId  = lastId.Id
		self.Id = lastId + 1
				
		if sell:
			self.builder    = get_builder("SellingForm")
		else:
			self.builder    = get_builder("BuyingForm")

		self.window = self.builder.get_object("viewWindow")
	#	self.window.set_skip_taskbar_hint(True)
		
		###editing
		
		self.factorDate = DateEntry()
		self.builder.get_object("datebox").add(self.factorDate)
		self.factorDate.show()
		self.product = None
		self.shippedDate = DateEntry()
		self.builder.get_object("shippedDateBox").add(self.shippedDate)
		self.shippedDate.show()
		
		
		#edit date
		self.editDate = DateEntry().getDateObject()
		
		self.additionsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("additionsbox").add(self.additionsEntry)
		self.additionsEntry.set_alignment(0.95)
		self.additionsEntry.connect("changed", self.valsChanged)
		
		self.subsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("subsbox").add(self.subsEntry)
		self.subsEntry.set_alignment(0.95)
		self.subsEntry.connect("changed", self.valsChanged)
		
		self.cashPymntsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("cashbox").add(self.cashPymntsEntry)
		self.cashPymntsEntry.set_alignment(0.95)	
		self.cashPymntsEntry.connect("changed", self.paymentsChanged)
		
		self.qntyEntry = decimalentry.DecimalEntry()
		self.builder.get_object("qntyBox").add(self.qntyEntry)
		#self.qntyEntry.show()
		self.qntyEntry.connect("focus-out-event", self.validateQnty)
		
		self.unitPriceEntry = decimalentry.DecimalEntry()
		self.builder.get_object("unitPriceBox").add(self.unitPriceEntry)
		self.unitPriceEntry.connect("focus-out-event", self.validatePrice)

		self.discountEntry = decimalentry.DecimalEntry()
		self.builder.get_object("unitDiscBox").add(self.discountEntry)
		self.discountEntry.connect("focus-out-event", self.validateDiscnt)
		
		self.customerEntry      = self.builder.get_object("customerCodeEntry")
		self.totalEntry         = self.builder.get_object("subtotalEntry")
		self.totalDiscsEntry    = self.builder.get_object("totalDiscsEntry")
		self.payableAmntEntry   = self.builder.get_object("payableAmntEntry")
		self.totalPaymentsEntry = self.builder.get_object("totalPaymentsEntry")
		self.remainedAmountEntry= self.builder.get_object("remainedAmountEntry")
		self.nonCashPymntsEntry = self.builder.get_object("nonCashPymntsEntry")
		self.customerNameEntry  = self.builder.get_object("customerNameEntry")
		self.taxEntry           = self.builder.get_object("taxEntry")
		self.feeEntry           = self.builder.get_object("feeEntry")
		
		self.treeview = self.builder.get_object("TreeView")		# factors List
		self.treestore = Gtk.TreeStore(int, str, str, str, str,str,str)
		self.treestore.clear()
		self.treeview.set_model(self.treestore)
		
					
		column = Gtk.TreeViewColumn(_("Id"), Gtk.CellRendererText(), text = 0)
		column.set_spacing(5)
		column.set_resizable(True)
		#column.set_sort_column_id(0)
		#column.set_sort_indicator(True)
		self.treeview.append_column(column)
		
		
		column = Gtk.TreeViewColumn(_("Factor"), Gtk.CellRendererText(), text = 1)
		column.set_spacing(4)
		column.set_resizable(True)
		column.set_sort_column_id(0)
		column.set_sort_indicator(True)
		self.treeview.append_column(column)		

		column = Gtk.TreeViewColumn(_("Doc."), Gtk.CellRendererText(), text = 2)
		column.set_spacing(3)
		column.set_resizable(True)
		column.set_sort_column_id(0)
		column.set_sort_indicator(True)
		self.treeview.append_column(column)
		
		column = Gtk.TreeViewColumn(_("Date"), Gtk.CellRendererText(), text = 3)
		column.set_spacing(5)
		column.set_resizable(True)
# 		column.set_sort_column_id(1)
# 		column.set_sort_indicator(True)
		self.treeview.append_column(column)		
		
		column = Gtk.TreeViewColumn(_("Customer"), Gtk.CellRendererText(), text = 4)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)	
		
		column = Gtk.TreeViewColumn(_("Total"), Gtk.CellRendererText(), text = 5)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)		

		column = Gtk.TreeViewColumn(_("Pre Invoice"), Gtk.CellRendererText(), text = 6)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)	
		
		self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
		#self.treestore.set_sort_func(0, self.sortGroupIds)
		self.treestore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.builder.connect_signals(self)	
		###editing		
		
			
	
		self.factorTreeView = self.builder.get_object("FactorTreeView")	# factor items list
		self.sellListStore = Gtk.TreeStore(str,str,str,str,str,str,str,str,int)
		self.sellListStore.clear()
		self.factorTreeView.set_model(self.sellListStore)
		
		headers = (_("No."), _("Product Name"), _("Quantity"), _("Unit Price"), 
				   _("Total Price"), _("Unit Disc."), _("Disc."), _("Description"))
		txt = 0
		for header in headers:
			column = Gtk.TreeViewColumn(header,Gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.factorTreeView.append_column(column)
			txt += 1
		
		self.sellsItersDict  = {}
		self.paysItersDict   = {}

		self.redClr = Gdk.color_parse("#FFCCCC")
		self.whiteClr = Gdk.color_parse("#FFFFFF")
	
	def viewSells(self,sender=0):
		self.treestore.clear()
		query = config.db.session.query(Factors,Customers)
		query = query.select_from(outerjoin(Factors,Customers, Factors.Cust == Customers.custId))
		query = query.order_by(Factors.Code.asc())
		query =	query.filter(Factors.Sell==self.sell).filter(Factors.Activated==1)
		result = query.all()

		self.cal = calverter()
		for t ,c in reversed(result):		
			date = t.tDate
			date = dateToString(date)
			pre_invoice = _("pre-invoice") if not t.Permanent else "-"
			bill_id = "-"			
			bill = config.db.session.query(Bill).select_from(Notebook).filter(Notebook.factorId == t.Id).filter(Notebook.bill_id == Bill.id).first()
			if bill:
				bill_id = str( bill.id) 			
			grouprow = self.treestore.append(None, (int(t.Id),utility.readNumber(t.Code),utility.readNumber(bill_id), date, c.custName, utility.LN(t.PayableAmnt) , pre_invoice))
			
		self.window.show_all()

		if self.sell:
			if utility.checkPermission(32):
				self.builder.get_object("addSelltn").hide()
			if utility.checkPermission(128):
				self.builder.get_object("editGroupsBtn").hide()
			if utility.checkPermission(256):
				self.builder.get_object("deleteGroupBtn").hide()
		else:
			if utility.checkPermission(32):
				self.builder.get_object("addBuyButton").hide()
			if utility.checkPermission(128):
				self.builder.get_object("editBuyButton").hide()
			if utility.checkPermission(256):
				self.builder.get_object("deleteBuyButton").hide()
		
	def on_add_clicked(self,sender):
		self.addNew()
							
	def addNew(self,transId=None):   # add sell			
		if self.editFlag:			
			self.Id	= self.editTransaction.Id
			self.Code 	= self.editTransaction.Code									
		else : 
			query   = self.session.query(Factors)
			last  = query.order_by(Factors.Id.desc()).first()
			if not last:				
				self.Code  = 1
				self.Id = 1				
			else:
				self.Id = int(last.Id) + 1
				lastFactor = query.filter(Factors.Sell == self.sell).order_by(Factors.Code.desc()).first()
				if lastFactor:										
					self.Code  = int(lastFactor.Code) + 1						
				else :										
					self.Code = 1					
		self.mainDlg = self.builder.get_object("FormWindow")

		self.Codeentry = self.builder.get_object("transCode")
		self.Codeentry.set_text(LN(self.Code))
		self.statusBar  = self.builder.get_object("FormStatusBar")	

		
		self.paymentManager = payments.Payments(transId=self.Id, sellFlag = self.sell)
		self.paymentManager.connect("payments-changed", self.setNonCashPayments)
		self.paymentManager.fillPaymentTables()
		self.paymentManager.customerNameLbl.set_text(self.customerNameEntry.get_text())		
		self.paymentManager.payerEntry.set_text(self.customerEntry.get_text())		

		self.sellListStore.clear()
		if transId:
			sellsQuery  = self.session.query(FactorItems)
			sellsQuery  = sellsQuery.filter(FactorItems.factorId==transId).order_by(FactorItems.number.asc()).all()
			for sell in sellsQuery:				
				ttl     = sell.untPrc * sell.qnty
				disc    = sell.untDisc * sell.qnty				
				list    = (utility.readNumber(sell.number,sell.productId,sell.qnty,utility.LN(sell.untPrc),utility.LN(ttl),utility.LN(sell.untDisc),str(disc),sell.desc,sell.productId) )
				self.sellListStore.append(None,list)
		
		
		if self.editFlag:										
			saveBtn = "fullFactorSellBtn" if self.sell else "fullFactorBuyBtn"		
			self.builder.get_object(saveBtn).set_label(_("Save Changes") )			
			
			self.Codeentry = self.builder.get_object("transCode")
			if config.digittype == 1:
				self.Codeentry.set_text(utility.convertToPersian(str(self.editTransaction.Code)))				
			else:
				self.Codeentry.set_text(str(self.editTransaction.Code))			
									
			query = self.session.query(Customers).select_from(Customers)
			customer = query.filter(Customers.custId == self.editTransaction.Cust).first()						
			self.sellerSelected(self, self.editTransaction.Cust,customer.custCode)	
					
			query=self.session.query(FactorItems).select_from(FactorItems)
			factorItems = query.filter(FactorItems.factorId==self.editTransaction.Id).all()
			self.oldProductList = factorItems
			number=1
			for factorItem in factorItems:						
				query=self.session.query(Products).select_from(Products)
				product = query.filter(Products.id==factorItem.productId).first()
				sellList = (utility.readNumber(number), product.name, utility.LN(factorItem.qnty), utility.LN(factorItem.untPrc),\
						 utility.LN(factorItem.qnty*factorItem.untPrc), utility.LN(factorItem.untDisc),\
						 utility.LN(float(factorItem.qnty)*float(factorItem.untDisc)), factorItem.desc,factorItem.productId) 
				self.sellsItersDict[number] =  self.sellListStore.append(None,sellList)				
				self.appendPrice(factorItem.qnty*factorItem.untPrc)
				self.appendDiscount(float(factorItem.qnty)*float(factorItem.untDisc))
				self.valsChanged()
				number+=1																
			self.taxEntry.set_text(str(utility.LN(self.editTransaction.VAT)))
			self.feeEntry.set_text(str(utility.LN(self.editTransaction.Fee)))
			self.additionsEntry.set_text(str(utility.LN(self.editTransaction.Addition)))
			self.subsEntry.set_text(str(utility.LN(self.editTransaction.Subtraction)))			
			
			self.cashPymntsEntry.set_text(utility.LN(self.editTransaction.CashPayment))	
			self.builder.get_object("shipViaEntry").set_text(str(self.editTransaction.ShipVia))
			self.builder.get_object("transDescEntry").set_text(str(self.editTransaction.Desc))
			self.factorDate.set_text(str(self.editTransaction.tDate))			
			self.factorDate.showDateObject(self.editTransaction.tDate)	
			self.shippedDate.set_text(str(self.editTransaction.ShipDate))			
			self.shippedDate.showDateObject(self.editTransaction.ShipDate)
			self.builder.get_object("preChkBx").set_active(self.editTransaction.Permanent ^ 1)

		self.mainDlg.show_all()

											
	def editSelling(self,  treeview=None, path=None, view_column = None):  # both sell and buy
		self.editFlag=True		
		selection = self.treeview.get_selection()
		iter = selection.get_selected()[1]		
		code = self.treestore.get_value(iter, 0) 		
		query = config.db.session.query(Factors, Customers)
		query = query.select_from(outerjoin(Factors, Customers, Factors.Cust== Customers.custId))
		result,result2 = query.filter(Factors.Id == code).first() 		
		self.editTransaction=result
		self.customer=result2
		self.addNew() 		
																						
	def removeFactor(self, sender):
		selection = self.treeview.get_selection()
		iter1 = selection.get_selected()[1]	
		if iter == None :
			return
		else:
			msgbox = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, _("Are you sure to remove this row?"))
			msgbox.set_title(_("Are you sure?"))
			result = msgbox.run();
			msgbox.destroy() 
			if result != Gtk.ResponseType.OK : 
				return 			
		code = self.treestore.get_value(iter1, 0)	
		factor = config.db.session.query(Factors).filter(Factors.Id ==unicode(code) ).first()
		TransactionId = factor  . Id		
		
		#correcting products' count table		
		factorItems=self.session.query(FactorItems) . filter(FactorItems.factorId==TransactionId).all()		
		for factorItem in factorItems:
			product=self.session.query(Products) .filter(Products.id==factorItem.productId).first()			
			if self.sell:
				product.quantity+=factorItem.qnty
			else:
				product.quantity-=factorItem.qnty
			config.db.session.delete(factorItem)

		self.paymentManager = payments.Payments(transId=self.Id, sellFlag = self.sell)
		cheques = self.session.query(Cheque) . filter(Cheque.chqTransId == factor.Id).all()
		for ch in cheques :
			self.paymentManager.removeCheque(ch)		
		#removing notebooks					
		notebooks = self.session.query(Notebook) . filter(Notebook.factorId == factor.Id ).all()
		if len(notebooks):
			bill_id = notebooks[0].bill_id
			for nb in notebooks:
				self.session.delete(nb)		
			#removing related bill
			self.session.delete( self.session.query(Bill).filter(Bill.id == bill_id).first() )

		Transaction = config.db.session.query(Factors).filter(Factors.Id ==unicode(code) ).first()		 
		config.db.session.delete(Transaction)
		config.db.session.commit()
		self.treestore.remove(iter1)	

	def selectCustomers(self,sender=0):
		customer_win = customers.Customer()
		customer_win.viewCustomers()
		code = self.customerEntry.get_text()
		#if code != '':
		#	customer_win.highlightCust(code)  		# this function is empty !
		customer_win.connect("customer-selected", self.sellerSelected)
		
	def sellerSelected(self, sender, id, code):		
		self.customerEntry.set_text(code)
		sender.window.destroy()		
		self.setCustomerName()
				
	def setCustomerName(self, sender=0, ev=0):
		ccode = unicode(self.customerEntry.get_text())
		query = self.session.query(Customers).select_from(Customers)
		customer = query.filter(Customers.custCode == ccode).first()
		if customer:
			self.customerNameEntry.set_text(customer.custName)
			self.paymentManager.customerNameLbl.set_text(customer.custName)
		else:
			self.customerNameEntry.set_text("")		

	def selectProduct(self,sender=0):
		obj = product.Product()
		obj.viewProducts()
		obj.connect("product-selected",self.proSelected)
		code = self.proVal.get_text()
		group = self.productGroup.get_text()
		obj.highlightProduct(unicode(code) , unicode(group))

	def proSelected(self,sender=0, id=0, code=0):
		code = unicode(code)		
		selectedPro = self.session.query(Products).filter(Products.id==id).first()		
		id      = selectedPro.id
		code    = selectedPro.code
		name    = selectedPro.name
		av_qnty    = selectedPro.quantity
		sellPrc = selectedPro.sellingPrice
		purchacePrc = selectedPro.purchacePrice
		formula  = selectedPro.discountFormula
		accGroup = selectedPro.accGroup
		qnty = self.qntyEntry.get_float()
		discnt = self.calcDiscount(formula, qnty, sellPrc)
		
		self.product = selectedPro
		self.avQntyVal.set_text(utility.LN(av_qnty))
		self.stnrdDisc.set_text(utility.LN(discnt))

		if self.sell:
			self.unitPriceEntry.set_text(utility.LN(sellPrc, comma=False))
		else:
			self.unitPriceEntry.set_text(utility.LN(purchacePrc, comma=False))

		self.discountEntry.set_text(utility.LN(discnt, comma=False))
		self.stndrdPVal.set_text(utility.LN(sellPrc))
		self.productGroup .set_text(unicode(accGroup))
		self.proNameLbl.set_text(unicode(name))
		self.proNameLbl.show()
		
		self.avQntyVal.show()
		self.stnrdDisc.show()
		self.stndrdPVal.show()
		
		if sender:
			self.proVal.set_text(unicode(code))
			sender.window.destroy()

	def addProduct(self,sender=0,edit=None):
		self.addDlg = self.builder.get_object("addDlg")
		self.edtSellFlg = False
		if edit:
			self.editCde    = edit[0]
			ttl = _("Edit sell:\t%s - %s") %(self.editCde,edit[1]) 
			self.addDlg.set_title(ttl)
			self.edtSellFlg = True		#TODO find usage
			self.oldTtl     = utility.getFloat(edit[4])
			self.oldTtlDisc = utility.getFloat(edit[6])
			btnVal  = _("Save Changes...")
		else:
			self.editingSell    = None
			if self.sell:
				self.addDlg.set_title(_("Choose sell information") )
			else:
				self.addDlg.set_title(_("Choose buy information"))
			
			btnVal  = _("Add to list")
		
		self.proVal        = self.builder.get_object("proEntry")		# product's Code
		self.productGroup  = self.builder.get_object("lblAccGroup")
		#self.discountEntry = self.builder.get_object("discountEntry")
		self.descVal       = self.builder.get_object("descVal")
		self.proNameLbl    = self.builder.get_object("proNameLbl")
		self.avQntyVal     = self.builder.get_object("availableQntyVal")
		self.stnrdDisc     = self.builder.get_object("stnrdDiscVal")
		self.stndrdPVal    = self.builder.get_object("stnrdSelPrceVal")
		self.discTtlVal    = self.builder.get_object("discTtlVal")
		self.ttlAmntVal    = self.builder.get_object("totalAmontVal")
		self.ttlPyblVal    = self.builder.get_object("totalPyableVal")
		
		self.btn        = self.builder.get_object("okBtn")
		self.btn.set_label(btnVal)
		self.addStBar   = self.builder.get_object("addStatusBar")
		self.addStBar.push(1,"")
		
		self.proVal.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
		self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
		self.unitPriceEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
		self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
		
		if self.edtSellFlg:
			(No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc,pId) = edit
			pId = unicode(pId)
			pName   = unicode(pName)
			pro = self.session.query(Products).filter(Products.id==pId).first()
			self.proVal.set_text(pro.code)
			self.product_code = pro.code
			
			self.qntyEntry.set_text(qnty)
			self.quantity = utility.getFloat(qnty)
			
			self.unitPriceEntry.set_text(untPrc.replace(',', ''))
			self.discountEntry.set_text(untDisc.replace(',', ''))
			self.descVal.set_text(desc)
			
			self.proNameLbl.set_text(pName)
			self.productGroup.set_text(unicode(pro.accGroup))
			self.avQntyVal.set_text(utility.LN(pro.quantity))
			self.stndrdPVal.set_text(utility.LN(pro.sellingPrice))
			
			self.ttlAmntVal.set_text(ttlPrc) 
			self.discTtlVal.set_text(ttlDisc) 
			total_payable = utility.getFloat(ttlPrc) - utility.getFloat(ttlDisc)
			discval = self.calcDiscount(pro.discountFormula, utility.getFloat(qnty), 
										pro.sellingPrice)
			self.ttlPyblVal.set_text(utility.LN(total_payable))
			self.stnrdDisc.set_text(utility.LN(discval))
			self.product = pro
			
		else:
			self.clearSellFields()
			self.product_code = ""
			self.quantity = 0
			
		self.addDlg.show_all()
				
	def editProduct(self,sender=None , treeview=None , path = None):
		iter    = self.factorTreeView.get_selection().get_selected()[1]
		if iter != None :
			self.editingSell    = iter
			No      = self.sellListStore.get(iter, 0)[0]
			pName   = self.sellListStore.get(iter, 1)[0]
			qnty    = self.sellListStore.get(iter, 2)[0]
			untPrc  = self.sellListStore.get(iter, 3)[0]
			ttlPrc  = self.sellListStore.get(iter, 4)[0]
			untDisc = self.sellListStore.get(iter, 5)[0]
			ttlDisc = self.sellListStore.get(iter, 6)[0]
			desc    = self.sellListStore.get(iter, 7)[0]
			id    = self.sellListStore.get(iter, 8)[0]			
			edtTpl  = (No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc,id)
			self.addProduct(edit=edtTpl)
		
	def removeProduct(self,sender):
		delIter = self.factorTreeView.get_selection().get_selected()[1]
		if delIter:
			No  = unicode(self.sellListStore.get(delIter, 0)[0])
			msg = _("Are You sure you want to delete the sell row number %s?") %No
			msgBox  = Gtk.MessageDialog( self.mainDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, msg)
			msgBox.set_title(_("Confirm Deletion"))
			answer  = msgBox.run()
			msgBox.destroy()
			if answer != Gtk.ResponseType.OK:
				return
			ttlPrc  = utility.getFloat(self.sellListStore.get(delIter,4)[0])
			ttlDisc = utility.getFloat(self.sellListStore.get(delIter,6)[0])
			self.reducePrice(ttlPrc)
			self.reduceDiscount(ttlDisc)
			self.sellListStore.remove(delIter)
			self.valsChanged()
			No = utility.getInt(No)
			length  = len(self.sellsItersDict) -1
			if len(self.sellsItersDict) > 1:
				while No < length:			
					nextIter    = self.sellsItersDict[No+1]
					self.sellListStore.set_value(nextIter,0,str(No))
					self.sellsItersDict[No] = nextIter
					del self.sellsItersDict[No+1]
					No  += 1		
			else:
				self.sellsItersDict = {}
				
	def upProInList(self,sender):
		if len(self.sellsItersDict) == 1:
			return
		iter    = self.factorTreeView.get_selection().get_selected()[1]
		if iter:
			No   = utility.getInt(self.sellListStore.get(iter, 0)[0])
			abvNo   = No - 1			
			if abvNo > 0:
				aboveIter   = self.sellsItersDict[abvNo]
				self.sellListStore.move_before(iter,aboveIter)
				self.sellsItersDict[abvNo]  = iter
				self.sellsItersDict[No]     = aboveIter
				self.sellListStore.set_value(iter,0,str(abvNo))
				self.sellListStore.set_value(aboveIter,0,str(No))

	def downProInList(self,sender):
		if len(self.sellsItersDict) == 1:
			return
		iter    = self.factorTreeView.get_selection().get_selected()[1]
		if iter:
			No   = utility.getInt(self.sellListStore.get(iter, 0)[0])
			blwNo   = No + 1
			if No < len(self.sellsItersDict):
				belowIter   = self.sellsItersDict[blwNo]
				self.sellListStore.move_after(iter,belowIter)
				self.sellsItersDict[blwNo]  = iter
				self.sellsItersDict[No]     = belowIter
				self.sellListStore.set_value(iter,0,str(blwNo))
				self.sellListStore.set_value(belowIter,0,str(No))
								
	def cancelProduct(self,sender=0,ev=0):
		self.clearSellFields()
		self.addDlg.hide()
		return True
			
	def addProToList(self,sender=0):
		proCd   = unicode(self.proVal.get_text())
		product   = self.session.query(Products).filter(and_(Products.code==proCd ,Products.accGroup==unicode(self.productGroup.get_text() ) )).first()
		if not product:
			errorstr = _("The \"Product Code\" which you selected is not a valid Code.")
			msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, errorstr )
			msgbox.set_title(_("Invalid Product Code"))
			msgbox.run()
			msgbox.destroy()
			return
		
		productName = product.name
		purchasePrc = product.purchacePrice
		qnty    = self.qntyEntry.get_float()
		over    = product.oversell
		avQnty  = product.quantity
		productQuantityWarning = product.qntyWarning
		if qnty <= 0:
			errorstr = _("The \"Quantity\" Must be greater than 0.")
			msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, errorstr )
			msgbox.set_title(_("Invalid Quantity"))
			msgbox.run()
			msgbox.destroy()
			return
		elif qnty > avQnty:
			if not over:
				errorstr = _("The \"Quantity\" is larger than the storage, and over-sell is off!")
				errorstr += _("\nQuantity can be at most %s.") %avQnty
				msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
											Gtk.ButtonsType.OK, errorstr )
				msgbox.set_title(_("Invalid Quantity"))
				msgbox.run()
				msgbox.destroy()
		elif productQuantityWarning > (avQnty - qnty):
			errorstr = _("The \"Quantity\" is low!")
			msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, errorstr )
			msgbox.set_title(_("Quantity Warning"))
			msgbox.run()
			msgbox.destroy()
				
		slPrc   = self.unitPriceEntry.get_float()
		if slPrc <= 0:
			errorstr = _("The \"Unit Price\" Must be greater than 0.")
			msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, errorstr )
			msgbox.set_title(_("Invalid Unit Price"))
			msgbox.run()
			msgbox.destroy()
			return
			
		if slPrc < purchasePrc:
			msg     = _("The Unit Sell Price you entered is less than the product Purchase Price!\"")
			msgBox  = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION,
											Gtk.ButtonsType.OK_CANCEL, msg                             )
			msgBox.set_title(               _("Are you sure?")              )
			answer  = msgBox.run(                                           )
			msgBox.destroy(                                                 )
			if answer != Gtk.ResponseType.OK:
				return

				
		headers = ("Code","Product Name","Quantity","Unit Price","Unit Discount","Discount","Total Price","Description")
		#----values:
		discnt  = self.discTtlVal.get_text()
		discnt_val = utility.getFloat(discnt)
		total   = qnty*slPrc
		descp   = self.descVal.get_text()
		untDisc = self.discountEntry.get_text()
		if self.edtSellFlg:
			No  = self.editCde
			sellList    = (utility.readNumber(No),productName,utility.LN(qnty),utility.LN(slPrc),utility.LN(total), utility.LN(untDisc),discnt,descp , product.id)
			for i in range(len(sellList)):
				self.sellListStore.set(self.editingSell,i,sellList[i])
			
			self.appendPrice(total - self.oldTtl)
			self.appendDiscount(discnt_val - self.oldTtlDisc)
			self.valsChanged()
			self.sellsItersDict[No]   = self.editingSell
			self.addDlg.hide()
			
		else:
			No = len(self.sellsItersDict) + 1				
			No_str = utility.readNumber(No)
			qnty_str = utility.LN(qnty)
			slPrc_str = utility.LN(slPrc)
			total_str = utility.LN(total)
			untDisc = utility.LN(untDisc)
				
			sellList = (No_str, productName, qnty_str, slPrc_str, total_str, untDisc, discnt, descp, product.id )
			iter = self.sellListStore.append(None, sellList)
			self.appendPrice(total)
			self.appendDiscount(discnt_val)
			self.valsChanged()
			self.sellsItersDict[No]   = iter
			self.addDlg.hide()

	def appendPrice(self,  price):
		oldPrice    = utility.getFloat(self.totalEntry.get_text())
		totalPrce   = oldPrice + price
		self.totalEntry.set_text(utility.LN(totalPrce))

	def appendDiscount(self, discount):
		# oldDiscount = utility.getFloat(self.totalDiscsEntry.get_text())
		# oldDiscount = oldDiscount + float(discount) 
		self.listTotalDiscount += float(discount)
		self.totalDiscsEntry.set_text(utility.LN(self.listTotalDiscount))
												
	def reducePrice(self,  price):
		oldPrice    = utility.getFloat(self.totalEntry.get_text())
		totalPrce   = oldPrice - price
		self.totalEntry.set_text(utility.LN(totalPrce))

	def reduceDiscount(self, discount):
		# oldDiscount = utility.getFloat(self.totalDiscsEntry.get_text())
		# oldDiscount = oldDiscount - discount
		self.listTotalDiscount -= float(discount)
		self.totalDiscsEntry.set_text(utility.LN(self.listTotalDiscount))

					
	def clearSellFields(self):
		zerostr = "0"
		if config.digittype == 1:
			zerostr = utility.convertToPersian(zerostr)
			
		self.proVal.set_text("")
		self.qntyEntry.set_text(zerostr)
		self.unitPriceEntry.set_text(zerostr)
		self.discountEntry.set_text("")
		self.proNameLbl.set_text("")
		self.productGroup.set_text("")
		self.avQntyVal.set_text("")
		self.stnrdDisc.set_text("")
		self.stndrdPVal.set_text("")
		self.ttlAmntVal.set_text(zerostr)
		self.discTtlVal.set_text(zerostr)
		self.ttlPyblVal.set_text(zerostr)
		self.descVal.set_text("")
		

	def calculatePayable(self):
		dbconf = dbconfig.dbConfig()
		subtotal    = utility.getFloat(self.builder.get_object("subtotalEntry").get_text())
		ttlDiscs    = self.listTotalDiscount #+ utility.getFloat(self.builder.get_object("custDiscount").get_text())
		additions   = self.additionsEntry.get_float()
		subtracts   = self.subsEntry.get_float()
		taxEntry    = self.taxEntry
		feeEntry    = self.feeEntry

		self.totalDiscsEntry.set_text(utility.LN(ttlDiscs))
		self.totalFactor = subtotal + additions - subtracts - ttlDiscs	
		if self.vatCheck:
			self.VAT = self.totalFactor * dbconf.get_int("vat-rate")/100
			self.fee = self.totalFactor * dbconf.get_int("fee-rate")/100
			self.totalTax = self.VAT + self.fee

			taxEntry.set_text(utility.LN(str(self.VAT)))
			feeEntry.set_text(utility.LN(str(self.fee)))
		else:
			self.totalTax = 0
			self.VAT = 0
			self.fee = 0

		self.payableAmntEntry.set_text(utility.LN(self.totalFactor + self.totalTax))

	def calculateBalance(self):
		ttlPayment = utility.getFloat(self.totalPaymentsEntry.get_text())
		blnc = self.totalFactor + self.totalTax - ttlPayment
		self.remainedAmountEntry.set_text(utility.LN(blnc))
		
	
	def valsChanged(self,sender=0,ev=0):
		self.calculatePayable()
		self.calculateBalance()

	def validatePCode(self, sender, event):
		productCd   = unicode(self.proVal.get_text())
		productGroup = unicode(self.productGroup.get_text())
		if self.product_code != productCd:		
			product = self.session.query(Products).filter(and_(Products.id==productCd, Products.accGroup == productGroup ) ).first()
			if not product:
				self.proVal.modify_base(Gtk.StateType.NORMAL,self.redClr)
				msg = _("Product code is invalid")
				self.proVal.set_tooltip_text(msg)
				self.addStBar.push(1,msg)
				self.proNameLbl.set_text("")
				self.product = None
			else:
				self.proVal.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
				self.proVal.set_tooltip_text("")
				#self.proSelected(code=product.code)
				self.proNameLbl.set_text(unicode(product.name))
				self.productGroup.set_text(unicode(product.accGroup))
				self.product = product
			self.product_code = productCd
	
	def validateQnty(self, sender, event):
		if self.product:
			stMsg = ""
			severe = False
			
			if self.qntyEntry.get_text() == "":
				self.qntyEntry.set_text(utility.LN(0))
				qnty = 0
			else:
				qnty = self.qntyEntry.get_float()

			if self.quantity != qnty:		
				qntyAvlble  = float(self.product.quantity)
				over    = self.product.oversell
				if qnty < 0:
					self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					if not stMsg:
						stMsg  = _("Quantity must be greater than 0.")
						severe = True
					self.qntyEntry.set_tooltip_text(_("Quantity must be greater than 0.") )

				elif qnty > qntyAvlble and not over:
					self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					msg = _("Quantity is more than the available storage. (Over-Sell is Off)")
					if not stMsg:
						stMsg  = msg
						severe = False
					self.qntyEntry.set_tooltip_text(msg)

				else:
					self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
					self.qntyEntry.set_tooltip_text("")
					
				self.addStBar.push(1,stMsg)
				
				if not severe:
					code   = self.proVal.get_text()
					sellPrc = self.product.sellingPrice
					if self.product.discountFormula:			
						discval = self.calcDiscount(self.product.discountFormula, qnty, sellPrc)
						discstr = utility.LN(discval)
						if self.sell:
							self.discountEntry.set_text(discstr)
							self.stnrdDisc.set_text(discstr)
							self.calcTotalDiscount(discval)
					else:
						# if discount be expressed in percent, total discount is changed
						# by changing quantity.
						# calling validateDiscnt converts discount percentage into discount value,
						# then calculates total discount.
						self.validateDiscnt()
					
					self.calcTotal()
					
				self.quantity = qnty
				
	def validatePrice(self, sender, event):
		if self.product:
			stMsg = ""
			severe = False
			
			if self.unitPriceEntry.get_text() == "":
				untPrc = self.product.sellingPrice
				self.unitPriceEntry.set_text(utility.LN(untPrc, comma=False))
			else:
				untPrc  = self.unitPriceEntry.get_float()            
			
			if untPrc != None:
				purcPrc = self.product.purchacePrice
				if untPrc < 0:
					self.unitPriceEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					erMsg  = _("Unit Price cannot be negative.")
					self.unitPriceEntry.set_tooltip_text(erMsg)
					if not stMsg:
						stMsg   = erMsg
						severe = True

				elif untPrc < purcPrc:
					self.unitPriceEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					err  = _("Unit Price is less than the product purchase price.")
					self.unitPriceEntry.set_tooltip_text(err)
					if not stMsg:
						stMsg  = err

				else:
					self.unitPriceEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
					self.unitPriceEntry.set_tooltip_text("")
					
			self.addStBar.push(1,stMsg)
			if not severe:
				self.calcTotal()
	
	def validateDiscnt(self, sender=0, event=0):			
		if self.product:
			stMsg = ""
			severe = False
			
			purcPrc = self.product.purchacePrice
			untPrc = self.unitPriceEntry.get_float() 
			
			if self.discountEntry.get_text() == "":				
				self.discountEntry.set_text(self.stnrdDisc.get_text())
				discval = utility.getFloat(self.stnrdDisc.get_text())
			else:				
				disc  = utility.convertToLatin(self.discountEntry.get_text())
				discval = 0

				if disc != "":		
					pindex = disc.find(u'%')
					if pindex == 0 or pindex == len(disc) - 1:
						discp = float(disc.strip(u'%'))
						
						if discp > 100 or discp < 0:
							self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
							errMess  = _("Invalid discount range. (Discount must be between 0 and 100 percent)")
							self.discountEntry.set_tooltip_text(errMess)
							if not stMsg:
								stMsg  = errMess
								severe = True
						else:
							discval = untPrc * (discp / 100)
							
					elif pindex == -1:
						try:
							discval = float(disc)
						except ValueError:
							self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
							errMess  = _("Invalid discount. (Use numbers and percentage sign only)")
							self.discountEntry.set_tooltip_text(errMess)
					else:
						self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
						errMess  = _("Invalid discount. (Put percentage sign before or after discount amount)")
						self.discountEntry.set_tooltip_text(errMess)
						if not stMsg:
							stMsg  = errMess
							severe = True
							
			self.addStBar.push(1,stMsg)
			if not severe:
				if untPrc < discval:
					self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					errMess  = _("Applying discount decreases product price below its purchase price!")
					self.discountEntry.set_tooltip_text(errMess)
					if not stMsg:
						self.addStBar.push(1,errMess)
				else:
					self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
					self.discountEntry.set_tooltip_text("")				
				self.calcTotalDiscount(discval)


	def calcDiscount(self, formula, qnty, sell_price):
		discnt = 0
		flist = formula.split(u',')
		for elm in flist:
			if elm != '':
				partlist = elm.split(u':')
				numlist = partlist[0].split(u'-')
				if len(numlist) == 1:
					firstnum = float(numlist[0])
					if qnty > firstnum:
						discnt = float(partlist[1])
						continue
					elif qnty == firstnum:
						break
					else:
						break
				elif len(numlist) == 2:
					firstnum = float(numlist[0])
					secnum = float(numlist[1])
					if qnty > secnum:
						discnt = float(partlist[1])
						continue
					elif qnty < firstnum:
						break
					else:
						discnt = float(partlist[1])
		return discnt
						
	def calcTotal(self):
		unitPrice   = self.unitPriceEntry.get_float()
		qnty        = self.qntyEntry.get_float()
		total       = unitPrice * qnty
		self.ttlAmntVal.set_text(utility.LN(total))
		self.calcTotalPayable()

	def calcTotalDiscount(self, discount):
		qnty        = self.qntyEntry.get_float()
		totalDisc   = discount * qnty
		self.discTtlVal.set_text(utility.LN(totalDisc))
		self.calcTotalPayable()

	def calcTotalPayable(self):
		ttlAmnt = utility.getFloat(self.ttlAmntVal.get_text())
		ttldiscount = utility.getFloat(self.discTtlVal.get_text())
		self.ttlPyblVal.set_text(utility.LN(ttlAmnt - ttldiscount))

	def paymentsChanged(self, sender=0, ev=0):
		ttlCash = self.cashPymntsEntry.get_float()
		self.cashPayment = ttlCash
		ttlNonCash  = utility.getFloat(self.nonCashPymntsEntry.get_text())		
		ttlPayments = ttlCash + ttlNonCash
		
		self.totalPaymentsEntry.set_text(utility.LN(ttlPayments))
		self.calculateBalance()

		
	def showPayments(self,sender):				
		self.paymentManager.showPayments()
		self.ttlNonCashEntry = self.builder.get_object("ttlNonCashEntry")

	def submitFactorPressed(self,sender):		
		permit  = self.checkFullFactor()
		self.sell_factor = True
		if permit:
			self.registerTransaction()
			self.registerFactorItems()			
			if not self.subPreInv:
				self.registerDocument()			
			self.mainDlg.hide()	
			if self.window.props.visible:				
				self.viewSells()			
				
	def checkFullFactor(self):
						
		#self.subCust    = self.customerEntry.get_text()
		cust_code = unicode(self.customerEntry.get_text())
		query = self.session.query(Customers).select_from(Customers)
		cust = query.filter(Customers.custCode == cust_code).first()
		if not cust:
			msg = _("The customer code you entered is not valid.")
			self.statusBar.push(1, msg)
			return False
		else:
			self.custId  = cust.custId
			self.custSubj = cust.custSubj
								
		if len(self.sellListStore)<1:
			self.statusBar.push(1, _("There is no product selected for the invoice.") )
			return False
						
		self.subCode    = self.Code
		
		self.subDate    = self.factorDate.getDateObject()
		self.subPreInv  = self.builder.get_object("preChkBx").get_active()
		
		if not self.subPreInv:
			pro_dic = {}
			for exch in self.sellListStore:
				pro_id = unicode(exch[8])
				pro_qnty = utility.getFloat(exch[2])
				
				if pro_id in pro_dic:
					pro_dic[pro_id] -= pro_qnty
				else:					
					query   = self.session.query(Products).filter(Products.id == pro_id)
					pro = query.first()
					if not pro.oversell:
						pro_dic[pro_id] = pro.quantity - pro_qnty
			
			pro_str = ""
			for (k, v) in pro_dic.items():	
				if v < 0:
					pro_str += k + _(", ")
					
			pro_str.strip()		
			
			if pro_str:
				msg = _("The available quantity of %s is not enough for the invoice. You can save it as pre-invoice.") \
						% pro_str
				self.statusBar.push(1, msg)
				return False
									
		self.subAdd     	= self.additionsEntry.get_float()
		self.subSub     	= self.subsEntry.get_float()
		self.subShpDate 	= self.shippedDate.getDateObject()		
		self.subShipVia 	= unicode(self.builder.get_object("shipViaEntry").get_text())
		self.subDesc    	= unicode(self.builder.get_object("transDescEntry").get_text())	
		self.totalFactor 	= utility.getFloat(self.payableAmntEntry.get_text())
		self.totalDisc 		= utility.getFloat(self.totalDiscsEntry.get_text())
		self.totalPayment 	= utility.getFloat(self.totalPaymentsEntry.get_text())
		self.statusBar.push(1,"")
		return True

	def registerTransaction(self):
		permanent = self.subPreInv ^ 1
		if self.editFlag:
			query=self.session.query(Factors)
			factor=query.filter(Factors.Code==self.subCode)
			factor = factor.filter(Factors.Sell == self.sell)

			'''Factors.Delivery: self.subFOB  ,'''
			factor.update({Factors.Cust : self.custId  , Factors.Addition : self.subAdd , Factors.Subtraction : self.subSub ,  Factors.VAT : self.VAT , Factors.CashPayment:self.cashPayment , Factors.ShipDate : self.subShpDate,
				 Factors.ShipVia : self.subShipVia , Factors.Permanent : permanent , Factors.Desc:self.subDesc , Factors.Sell: self.sell, Factors.Fee: self.fee , Factors.PayableAmnt : self.totalFactor,
				Factors.LastEdit : self.editDate  })

		else:
			'''self.subFOB,'''
			sell = Factors(self.subCode, self.subDate, 0, self.custId, self.subAdd, self.subSub, self.VAT, self.fee, self.totalFactor, self.cashPayment,
					self.subShpDate,'', self.subShipVia, permanent, self.subDesc, self.sell, self.subDate, 1)#editdate=subdate

			self.session.add(sell)
		#self.session.commit()
		query = config.db.session.query(Customers)
		query =	query.filter(Customers.custId==self.custId)
		customer = query.first()
		pre_invoice = "pre-invoice" if not permanent else ""		
		
	def registerFactorItems(self):	
			
		if self.editFlag:								 
			lasttransId = self.Id # Id of editing  factor

			# restore sold/bought products count
			for oldProduct in self.oldProductList: # The old product list
				foundFlag = False
				for exch in self.sellListStore: # The new sell list store
					#query = self.session.query(Products)
					#pid = query.filter(Products.name == unicode(exch[1])).first().id
					pid = exch[8]					
					if pid == oldProduct.productId:
						foundFlag = True
						break
				if not foundFlag:
					query   = self.session.query(Products).filter(Products.id == oldProduct.productId ) 
					pro = query.first()
					if self.sell:
						pro.quantity += oldProduct.qnty
					else:
						pro.quantity -= oldProduct.qnty
					self.session.query(FactorItems).filter(FactorItems.productId == oldProduct.productId).delete()					

		
		for exch in self.sellListStore: # The new sell list store
			pid = exch[8] #query.filter(Products.name == unicode(exch[1])).first().id			
			query = self.session.query(Products).filter(Products.id == pid)
			pro = query.first()			
			lastfactorItemquantity=utility.getFloat(0)
			nowfactorItemquantity=utility.getFloat(exch[2])

			if self.editFlag:
				Item=self.session.query(FactorItems)				
				Item=Item.filter(FactorItems.productId==pid)
				Item =Item.filter(FactorItems.factorId==self.Id)
				factorItem1 = Item.first()
				
				if (not factorItem1) or (self.editTransaction.Permanent == 0 and self.subPreInv == 0):
					lastfactorItemquantity=utility.getFloat(str(0))
					nowfactorItemquantity=utility.getFloat(exch[2])
					
					factorItem = FactorItems(utility.getInt(exch[0]), pid, utility.getFloat(exch[2]),
										 utility.getFloat(exch[3]), utility.convertToLatin(exch[5]),
										 self.Id, unicode(exch[7]))
					self.session.add( factorItem )									
					if self.sell:
						pro.quantity -= nowfactorItemquantity
					else:
						pro.quantity += nowfactorItemquantity							
				else:   #  product exists in factor
					lastfactorItemquantity = utility.getFloat(str(factorItem1.qnty))
					nowfactorItemquantity = utility.getFloat(exch[2])
					
					Item.update({FactorItems.number: utility.getInt(exch[0]) , FactorItems.productId : pid ,FactorItems.qnty: utility.getFloat(exch[2]) , 
						FactorItems.untPrc :utility.getFloat(exch[3]), 	 FactorItems.untDisc : utility.convertToLatin(exch[5]) , FactorItems.desc : unicode(exch[7]) })
					
					if lastfactorItemquantity != nowfactorItemquantity:												
						if self.sell:
							pro.quantity += lastfactorItemquantity - nowfactorItemquantity
						else:
							pro.quantity -= lastfactorItemquantity - nowfactorItemquantity						
					
			# in add mode transaction																						
			else:					
				lastfactorItemquantity=utility.getFloat(str(0))
				nowfactorItemquantity=utility.getFloat(exch[2])
				factorItem = FactorItems(utility.getInt(exch[0]), pid, utility.getFloat(exch[2]),
									 utility.getFloat(exch[3]), utility.convertToLatin(exch[5]),
									 self.Id, unicode(exch[7]))
				self.session.add( factorItem )									
							
				#---- Updating the products quantity
				#TODO product quantity should be updated while adding products to factor
				if not self.subPreInv:																	
					if self.sell:
						pro.quantity -= nowfactorItemquantity
					else:
						pro.quantity += nowfactorItemquantity
					
					lastfactorItemquantity=utility.getFloat(0)
					nowfactorItemquantity=utility.getFloat(0)
		self.session.commit()
					
		
	def registerDocument(self):
		cust_code = unicode(self.customerEntry.get_text())				
		cust = self.session.query(Customers).filter(Customers.custCode == cust_code).first()
		
		cl_cheque = class_cheque.ClassCheque()
		dbconf = dbconfig.dbConfig()
		for cheque in self.paymentManager.chequesList:
			if cheque.chqStatus == 5 :
				#cl_cheque.update_status(sp_cheque.chqId,5 , self.custId)
				self.Document.add_cheque(dbconf.get_int('other_cheque'),self.custSubj, -cheque.chqAmount , unicode(_('spended')) , cheque.chqId)
			elif not self.sell: #buying - our cheque
				self.Document.add_cheque(dbconf.get_int('our_cheque'),self.custSubj, cheque.chqAmount, cheque.chqDesc, cheque.chqId)
			else:		 	  #selling - their cheque
				self.Document.add_cheque(dbconf.get_int('other_cheque'),self.custSubj, -cheque.chqAmount, cheque.chqDesc, cheque.chqId) 

			##add cheque history			
			chequeHistoryChequeId 	= 	cheque.chqId
			chequeHistoryAmount   	=	cheque.chqAmount
			chequeHistoryWrtDate  	=	cheque.chqWrtDate
			chequeHistoryDueDate	=	cheque.chqDueDate
			chequeHistorySerial	    =	cheque.chqSerial
			chequeHistoryStatus	    =	cheque.chqStatus
			chequeHistoryCust		=	cust.custId
			chequeHistoryAccount	=	cheque.chqAccount
			chequeHistoryDesc		=	cheque.chqDesc
			chequeHistoryDate		=	self.editDate
			chequeHistoryTransId	=	self.Id					
			
			chequeHistory= ChequeHistory(			
						chequeHistoryChequeId 	,
						chequeHistoryAmount   	,
						chequeHistoryWrtDate  	,
						chequeHistoryDueDate	,
						chequeHistorySerial	,
						chequeHistoryStatus	,
						chequeHistoryCust		,
						chequeHistoryAccount	,
						chequeHistoryTransId	,
						chequeHistoryDesc		,
						chequeHistoryDate			)  
			self.session.add(chequeHistory) 
			self.session.commit()						
			ch = self.session.query(Cheque).filter(Cheque.chqId == cheque.chqId).first()			
			ch.chqHistoryId = chequeHistory.Id			
			self.session.commit()


		# Create new document
		bill_id = self.saveDocument()


		# for cheque in self.paymentManager.chequesList:								#CANREMOVE
		# 	notebook_id = self.Document.cheques_result[cheque.chqId]
		# 	ch = self.session.query(Cheque).filter(Cheque.chqId == cheque.chqId).first()
		# 	ch.chqNoteBookId = notebook_id					

		cheques = self.session.query(Cheque).filter(Cheque.chqTransId == self.Id ).all()
		for cheque in cheques: 
			cheque.chqCust = cust.custId 
		self.session.commit()														

		# Assign document to the current transaction
		# query = self.session.query(Factors)			#CANREMOVE
		# query = query.filter(Factors.Code == self.Code)
		# query = query.filter(Factors.Sell == self.sell)
		# query.update( {Factors.Bill : bill_id } )		#CANREMOVE
		# self.session.commit()	
			
			
	def createPrintJob(self):
		dbconf = dbconfig.dbConfig()
		date = self.editTransaction.tDate
		date = dateToString(date)
		if self.sell:
			factorSellerName = dbconf.get_value('co-name')
			factorSellerAddress = dbconf.get_value('co-address')
			factorSellerEconomicalCode = utility.convertToPersian(dbconf.get_value('co-economical-code'))
			factorSellerPostalCode = dbconf.get_value('co-name')
			factorSellerNationalCode = utility.convertToPersian(dbconf.get_value('co-national-code'))
			factorSellerPhoneNumber = utility.convertToPersian(dbconf.get_value('co-phone-number'))
			factorBuyerName = self.customer.custName
			factorBuyerAddress = self.customer.custAddress
			factorBuyerEconomicalCode = utility.convertToPersian(self.customer.custEcnmcsCode)
			factorBuyerPostalCode = utility.convertToPersian(self.customer.custPostalCode)
			factorBuyerNationalNum = utility.convertToPersian(self.customer.custPersonalCode)
			factorBuyerPhoneNumber = utility.convertToPersian(self.customer.custPhone)
		else:
			factorSellerName = utility.convertToPersian(self.customer.custName)
			factorSellerAddress = utility.convertToPersian(self.customer.custAddress)
			factorSellerEconomicalCode = utility.convertToPersian(self.customer.custEcnmcsCode)
			factorSellerPostalCode = utility.convertToPersian(self.customer.custPostalCode)
			factorSellerNationalCode = utility.convertToPersian(self.customer.custPersonalCode)
			factorSellerPhoneNumber = utility.convertToPersian(self.customer.custPhone)
			factorBuyerName = utility.convertToPersian(dbconf.get_value('co-name'))
			factorBuyerAddress = utility.convertToPersian(dbconf.get_value('co-address'))
			factorBuyerEconomicalCode = utility.convertToPersian(dbconf.get_value('co-economical-code'))
			factorBuyerPostalCode = utility.convertToPersian(dbconf.get_value('co-name'))
			factorBuyerNationalNum = utility.convertToPersian(dbconf.get_value('co-national'))
			factorBuyerPhoneNumber = utility.convertToPersian(dbconf.get_value('co-phone-number'))
		if self.editTransaction.Permanent:
			title = 'صورتحساب فروش کالا و خدمات'
			factorNumber = utility.LN(self.editTransaction.Code)
		else:
			title = 'پیش فاکتور'
			factorNumber = ''
		html = '<html> \
					<head> \
						<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> \
						<style>@font-face {font-family: Vazir; src: url(data/font/Vazir.woff); }\
							 .none{border:none;} .border{border:1px solid #000;} .right{text-align:right;direction:rtl;} .center{text-align:center !important;direction:rtl;} .pink{background-color:#ffe0eb;} \
							body,table {font-family: Vazir;font-size:15px; height:100%;} .bold{font-weight:bold; font-size:11px;} .lheight{line-height:1.7em;text-align:right;} \
							.date-number td{padding: 10px;} \
							.date-number {border-collapse: separate;}\
							@page {size: A4 landscape;margin: 3mm 3mm 3mm 3mm;} \
						</style> \
					</head> \
					<body> \
						<table style="table-layout:fixed; width:100%; height: 1px" class="date-number"> \
							<tbody> \
								<tr> \
									<td class="border right pink" style="width:19%;line-height: 0.9em;"><span style="color:#BB0000;">' + factorNumber +'</span>شماره: \
									</td> \
									<td rowspan="2" class="none" width="850" style="text-align:center"> \
										<p style="font-weight:bold;font-size:16px;">' + title + '</p> \
									</td> \
								</tr> \
								<tr> \
									<td class="border right pink"  style="line-height: 0.9em;">تاریخ: ' + date + '</td> \
								</tr> \
							</tbody> \
						</table> \
						<table cellspacing="0" cellpadding="8" style="table-layout:fixed;width:100%" class="mytable"> \
							<tbody> \
								<tr> \
									<td colspan="4" class="border center pink"> \
										<p align="center" class="bold" style="font-size:12px;height: 4px;">مشخصات فروشنده</p> \
									</td> \
								</tr> \
								<tr class="right"  style="height: 100px;"> \
									<td class="right none lheight" style="border-left:1px solid #000;"> \
										شماره ملی: ' + factorSellerNationalCode +'<br /> شماره تلفن: ' + factorSellerPhoneNumber + ' \
									</td> \
									<td class="right none lheight" > \
									 شماره اقتصادی: ' + factorSellerEconomicalCode + '<br /> کد پستی ۱۰ رقمی: ' + factorSellerPostalCode + ' \
									</td> \
									<td class="right none lheight"  width="27%"> \
										نام: ' + factorSellerName + ' <br />نشانی :  ' + factorSellerAddress + ' \
									</td> \
									<td class="right none" style="border-right:1px solid #000;width: 6%;"> <br> \
									</td> \
								</tr> \
								<tr> \
									<td class="pink center border" colspan="4" width="100%" valign="top"> \
										<p align="center" class="bold"  style="font-size:12px;height: 4px;">مشخصات خریدار</p> \
									</td> \
								</tr> \
								<tr class="right" style="height: 100px;"> \
									<td class="right none lheight" width="33%" style="border-left:1px solid #000;" > \
										شماره ملی: ' + factorBuyerNationalNum + '<br /> شماره تلفن: ' + factorBuyerPhoneNumber + ' \
									</td> \
									<td class="right none lheight" width="33%" > \
										شماره اقتصادی: ' + factorBuyerEconomicalCode + '<br /> کد پستی ۱۰ رقمی: ' + factorBuyerPostalCode + '\
									</td> \
									<td class="right none lheight" width="27%"> \
										نام: ' + factorBuyerName + '<br />نشانی :‌ ' + factorBuyerAddress + ' \
									</td> \
									<td class="right none" style="border-right:1px solid #000;width: 6%;"> <br> \
									</td> \
								</tr> \
							</tbody> \
						</table> \
						<table cellspacing="0" cellpadding="8" style="text-align:right;width:100%;border-collapse: collapse;"> \
							<tbody> \
								<tr valign="top" style="height: 4px;"> \
									<td class="border center" style="border-right: none;width:11%"> \
										<p align="center" class="bold">جمع مبلغ کل<br> \
										(ریال)</p> \
									</td> \
									<td class="border center" style="border-right: none;width:10%"> \
										<p align="center" class="bold">جمع مالیات و عوارض<br> \
										(ریال)</p> \
									</td> \
									<td class="border center" style="border-right: none;width:9%"> \
										<p align="center" class="bold">مبلغ کل پس از تخفیف<br> \
										(ریال)</p> \
									</td> \
										<td class="border center" style="border-right: none;width:9%"> \
										<p align="center" class="bold"> مبلغ تخفیف<br> \
										<br/>(ریال)</p> \
									</td> \
									<td class="border center" style="border-right: none;width:11%"> \
										<p align="center" class="bold">مبلغ کل<br> \
										(ریال)</p> \
									</td> \
									<td class="border center" style="border-right: none;width:11%"> \
										<p align="center" class="bold">مبلغ واحد<br> \
										(ریال)</p> \
									</td> \
									<td class="border center" style="border-right: none;width:5%"> \
										<p align="center" class="bold">واحد<br> \
										اندازه گیری</p> \
									</td> \
									<td class="border center" style="border-right: none;width:5%"> \
										<p align="center" class="bold">تعداد<br> \
										مقدار</p> \
									</td> \
									<td class="border center" style="border-right: none;width:26%"> \
										<p align="center" class="bold">شرح کالا یا خدمات</p> \
									</td> \
									<td class="border" style="border-right: none;width:2%"> \
										<p align="center" class="bold">کد<br> \
										کالا</p> \
									</td> \
									<td class="border"> \
										<div style="position: relative"> \
											<p style="text-align: center;" class="bold" style="width: 10px;">ردیف</p> \
										</div> \
									</td> \
								</tr>'

		k = 1;
		factor  = self.session.query(Factors).filter(Factors.Id == self.Id) . first()
		sellsQuery  = self.session.query(FactorItems, Products).select_from(FactorItems)
		sellsQuery  = sellsQuery.filter(FactorItems.factorId==self.Id, FactorItems.productId == Products.id).order_by(FactorItems.number.asc()).all()		
		sumTotalPrice = 0
		sumTotalDiscount = 0
		sumTotalAfterDiscount = 0
		sumTotalVat = factor.VAT + factor.Fee 
		totalVat = 0 
		sumFinalPrice = 0
		description = ''
		items = ''
		sell = None
		dbconf = dbconfig.dbConfig()
		for k in range(1 , len(sellsQuery) + 2 ) :			
			if k == len(sellsQuery) + 1 :	
				if not factor.Addition:
					if factor.Subtraction > 0 :
						productName = "تخفیف"
					else :
						break				
				else :
					productName = "سایر"
				productCode = "-"				
				quantity = 1
				unitPrice = float(factor.Addition)
				totalDiscount = factor.Subtraction				
			else:		
				sell = sellsQuery[k-1]						
				productCode = sell.Products.code
				productName = sell.Products.name 
				quantity = sell.FactorItems.qnty
				unitPrice = sell.FactorItems.untPrc
				totalDiscount = float(sell.FactorItems.untDisc) * float(sell.FactorItems.qnty)
			totalPrice = unitPrice * quantity			
			totalAfterDiscount = totalPrice - totalDiscount
			VAT = totalAfterDiscount * dbconf.get_int("vat-rate")/100
			Fee = totalAfterDiscount * dbconf.get_int("fee-rate")/100
			totalVat = VAT + Fee  #float(totalPrice) * 0.09
			finalPrice = totalAfterDiscount + totalVat

			sumTotalPrice += totalPrice
			sumTotalDiscount += totalDiscount
			sumTotalAfterDiscount += totalAfterDiscount
			#sumTotalVat += totalVat
			sumFinalPrice += finalPrice
			html +='<tr style="text-align:center; vertical-align: top;"> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(finalPrice)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" >\
							<span>' + utility.convertToPersian(str(totalVat)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(totalAfterDiscount)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(totalDiscount)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(totalPrice)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(unitPrice)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span style="text-align: right;">'+unicode(sell.Products.uMeasurement)+'</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(quantity)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(productName)) + '</span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span>' + utility.convertToPersian(str(productCode)) + '</span> \
						</td> \
						<td class="border"> \
							<span style="text-align: right;" class="bold" style="width: 10px;"> ' + utility.convertToPersian(str(utility.convertToPersian(k))) + ' </span> \
						</td> \
					</tr>'
			#k += 1
		for k in range(k, 7):
			html +='<tr style="text-align:center; vertical-align: top;"> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" >\
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span style="text-align: right;"></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border center" style="border-right: none;" > \
							<span></span> \
						</td> \
						<td class="border"> \
							<span style="text-align: right;" class="bold" style="width: 10px;"> ' + utility.convertToPersian(str(utility.convertToPersian(k))) + ' </span> \
						</td> \
					</tr>'
			k += 1
		html += '				<tr style="vertical-align: top;"> \
	        						<td class="border center" style="border-right: none;" width="9%"> \
	            						<span>' + utility.convertToPersian(str(sumFinalPrice)) + '</span> \
        							</td> \
	        						<td class="border center" style="border-right: none;" width="15%"> \
	            						<span align="right">' + utility.convertToPersian(str(sumTotalVat)) + '</span> \
	        						</td> \
	        						<td class="border center" style="border-right: none;" width="13%"> \
	            						<span align="right">' + utility.convertToPersian(str(sumTotalAfterDiscount)) + '</span> \
	        						</td> \
	        						<td class="border center" style="border-right: none;" width="7%"> \
	            						<span align="right">' + utility.convertToPersian(str(sumTotalDiscount)) + '</span> \
	        						</td> \
	        						<td class="border center" style="border-right: none;" width="7%"> \
	            						<span align="right">' + utility.convertToPersian(str(sumTotalPrice )) + '</span> \
	        						</td> \
	        						<td colspan="6" class="border pink center" width="49%"> \
	            						<span align="center">جمع کل (ریال): ' + utility.convertToPersian(str(sumTotalPrice)) + '</span> \
	        						</td> \
	    						</tr> \
	    						<tr valign="top"> \
	        						<td colspan="2" style="border: none; " width="24%"> \
	            						<span align="right">مهر و امضاء خریدار</span> \
	        						</td> \
	        						<td colspan="3" style="border: none; " width="32%"> \
	            						<span align="right">مهر و امضای فروشنده</span> \
	        						</td> \
	        						<td class="border" style="border-right: none;" width="9%"> \
	        						</td> \
	        						<td colspan="2" class="border" style="border-right: none;border-left:none;" width="17%"> \
	        						</td> \
	        						<td colspan="3" class="border" width="18%" style="border-left:none;height: 25px;"> \
	            						<span align="right" style="padding-right: 5px">شرایط و نحوه فروش:</span> \
	        						</td> \
	    						</tr> \
	    						<tr valign="top"> \
	        						<td colspan="5" style="border: none; " width="56%"> \
	            						<span align="right"><br></span> \
	        						</td> \
	        						<td colspan="6" class="border" width="44%" style="height: 25px;"> \
	            						<span style="padding-right: 5px">توضیحات: '+factor.Desc+'</span>  \
	        						</td> \
	    						</tr> \
							</tbody> \
						</table> \
					</body> \
				</html>'	
		return html
	def printTransaction(self, sender):
		
		if self.editFlag == False:  # adding 			
			self.submitFactorPressed(sender)
			query = config.db.session.query(Factors, Customers)
			query = query.select_from(outerjoin(Factors, Customers, Factors.Cust== Customers.custId))
			result,result2 = query.filter(Factors.Id == self.Id).first() 		
			self.editTransaction=result 
			self.customer=result2	
		else :
			self.submitFactorPressed(sender)

		self.reportObj = WeasyprintReport()
		printjob = self.createPrintJob()
		if printjob != None:
			# self.reportObj.doPrint(printjob, True)
			self.reportObj.showPreview(printjob, True)

	def setNonCashPayments(self, sender, str_value):
		self.nonCashPymntsEntry.set_text(str_value)
		self.paymentsChanged()

	def close(self, sender=0 , user_data = None):		
		self.session.rollback()		
		'''self.session.query(Cheque).filter(Cheque.chqTransId == self.Id).delete()
								self.session.query(Payment).filter(Payment.paymntTransId == self.Id).delete()
								self.session.commit()'''	
		self.mainDlg.hide()
		return True;

	def saveDocument(self):
		dbconf = dbconfig.dbConfig()
		# total = self.payableAmnt - self.totalDisc + self.subAdd + self.subTax
		
		trans_code = utility.LN(self.subCode, False)
		
		noteBookSell =  "sell" if self.sell  else "buy"
		sellN = (-1) ** (not self.sell )				
		self.Document.add_notebook(self.custSubj, -(self.totalFactor * sellN), _("Debit for invoice number %s") % trans_code,self.Id)
		if self.cashPayment:
			self.Document.add_notebook(self.custSubj, (self.cashPayment) * sellN, _("Cash Payment for invoice number %s") % trans_code,self.Id)
			self.Document.add_notebook(dbconf.get_int("cash"), -(self.cashPayment*sellN), _("Cash Payment for invoice number %s") % trans_code,self.Id)
		if self.subSub:
			self.Document.add_notebook(dbconf.get_int(noteBookSell+"-discount"), -(self.subSub)*sellN, _("Discount for invoice number %s") % trans_code,self.Id)
		if self.subAdd:
			self.Document.add_notebook(dbconf.get_int(noteBookSell+"-adds"), (self.subAdd) * sellN, _("Additions for invoice number %s") % trans_code,self.Id)
		if self.VAT:
			self.Document.add_notebook(dbconf.get_int(noteBookSell+"-vat"), (self.VAT) * sellN, _("VAT for invoice number %s") % trans_code,self.Id)
		if self.fee:
			self.Document.add_notebook(dbconf.get_int(noteBookSell+"-fee"), (self.fee)*sellN, _("Fee for invoice number %s") % trans_code,self.Id)
		if self.totalDisc:
			self.Document.add_notebook(dbconf.get_int(noteBookSell+"-discount"), -(self.totalDisc)*sellN, _("Discount on items for invoice number %s") % trans_code,self.Id)

		# Create a row for each sold product
		for exch in self.sellListStore:
			query = self.session.query(ProductGroups)
			query = query.select_from(outerjoin(Products, ProductGroups, Products.accGroup == ProductGroups.id))
			result = query.filter(Products.id == unicode(exch[8])).first()
			#sellid = result[0]
			sellid = result.sellId if self.sell else result.buyId

			exch_totalAmnt = utility.getFloat(exch[2]) * utility.getFloat(exch[3])
			#TODO Use unit name specified for each product
			if self.sell:
				self.Document.add_notebook(sellid, exch_totalAmnt, _("Selling %(units)s units, invoice number %(factor)s") % ({'units':exch[2], 'factor':trans_code}),self.Id)
			else:
				self.Document.add_notebook(sellid, -exch_totalAmnt, _("Buying  %(units)s units, invoice number  %(factor)s") % ({'units':exch[2], 'factor':trans_code}),self.Id)

		isTrueFactorId = self.Id  * self.editFlag   # 0 means inserting new factor and bill . otherwise is a valid factor ID
		docnum = self.Document.save(isTrueFactorId)
		share.mainwin.silent_daialog(_("Document saved with number %s.") % docnum)
		return docnum

	def vatCalc(self, sender=0, ev=0):
		self.vatCheck = self.builder.get_object("vatCheck").get_active()
		if not self.vatCheck:
			self.builder.get_object("taxEntry").set_text("0")
			self.builder.get_object("feeEntry").set_text("0")

		self.builder.get_object("taxEntry").set_sensitive(self.vatCheck)
		self.builder.get_object("feeEntry").set_sensitive(self.vatCheck)

		self.valsChanged()

