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
from gi.repository import Gtk
from gi.repository import Gdk


config = share.config

## \defgroup Controller
## @{

class Trade:
	"""Manage sell and buy form."""

	def __init__(self,sell = True, transId=None):
		self.sell = sell 	#Sell or buy
		self.addFalg = True
		self.editFalg = False
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
		
		query   = self.session.query(Trades.Id).select_from(Trades)
		lastId  = query.order_by(Trades.Id.desc()).first()			
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
		
		
		###editing
		
		self.factorDate = DateEntry()
		self.builder.get_object("datebox").add(self.factorDate)
		self.factorDate.show()
		
		self.shippedDate = DateEntry()
		self.builder.get_object("shippedDateBox").add(self.shippedDate)
		self.shippedDate.show()
		
		
		#edit date
		self.editDate = DateEntry().getDateObject()
		
		self.additionsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("additionsbox").add(self.additionsEntry)
		self.additionsEntry.set_alignment(0.95)
		#self.additionsEntry.show()
		self.additionsEntry.connect("changed", self.valsChanged)
		
		self.subsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("subsbox").add(self.subsEntry)
		self.subsEntry.set_alignment(0.95)
		#self.subsEntry.show()
		# self.subsEntry.set_sensitive(False)
		self.subsEntry.connect("changed", self.valsChanged)
		
		self.cashPymntsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("cashbox").add(self.cashPymntsEntry)
		self.cashPymntsEntry.set_alignment(0.95)
		#self.cashPymntsEntry.show()
		self.cashPymntsEntry.set_text("0")
		self.cashPymntsEntry.connect("changed", self.paymentsChanged)
		
		self.qntyEntry = decimalentry.DecimalEntry()
		self.builder.get_object("qntyBox").add(self.qntyEntry)
		#self.qntyEntry.show()
		self.qntyEntry.connect("focus-out-event", self.validateQnty)
		
		self.unitPriceEntry = decimalentry.DecimalEntry()
		self.builder.get_object("unitPriceBox").add(self.unitPriceEntry)
		#self.unitPriceEntry.show()
		self.unitPriceEntry.connect("focus-out-event", self.validatePrice)
		
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
		
		self.treeview = self.builder.get_object("TreeView")
		self.treestore = Gtk.TreeStore(int, str, str, str, str)
		self.treestore.clear()
		self.treeview.set_model(self.treestore)
		
					
		column = Gtk.TreeViewColumn(_("Id"), Gtk.CellRendererText(), text = 0)
		column.set_spacing(5)
		column.set_resizable(True)
		#column.set_sort_column_id(0)
		#column.set_sort_indicator(True)
		self.treeview.append_column(column)
		
		
		column = Gtk.TreeViewColumn(_("factor"), Gtk.CellRendererText(), text = 1)
		column.set_spacing(5)
		column.set_resizable(True)
 		column.set_sort_column_id(0)
 		column.set_sort_indicator(True)
		self.treeview.append_column(column)
		
		column = Gtk.TreeViewColumn(_("Date"), Gtk.CellRendererText(), text = 2)
		column.set_spacing(5)
		column.set_resizable(True)
# 		column.set_sort_column_id(1)
# 		column.set_sort_indicator(True)
		self.treeview.append_column(column)		
		
		column = Gtk.TreeViewColumn(_("Customer"), Gtk.CellRendererText(), text = 3)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)	
		
		column = Gtk.TreeViewColumn(_("Total"), Gtk.CellRendererText(), text = 4)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)		

		column = Gtk.TreeViewColumn(_("Permanent"), Gtk.CellRendererText(), text = 5)
		column.set_spacing(5)
		column.set_resizable(True)
		self.treeview.append_column(column)	
		
		self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
		#self.treestore.set_sort_func(0, self.sortGroupIds)
		self.treestore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
		self.builder.connect_signals(self)	
		###editing		
		
			
	
		self.sellsItersDict  = {}
		self.paysItersDict   = {}

		self.redClr = Gdk.color_parse("#FFCCCC")
		self.whiteClr = Gdk.color_parse("#FFFFFF")
		
	
	def viewSells(self,sender=0):
		query = config.db.session.query(Trades,Customers)
		query = query.select_from(outerjoin(Trades,Customers, Trades.Cust == Customers.custId))
		query = query.order_by(Trades.Code.asc())
		query =	query.filter(Trades.Sell==self.sell).filter(Trades.Acivated==1)
		result = query.all()

		for t ,c in reversed(result):		
	  		grouprow = self.treestore.append(None, (int(t.Id), t.Code, False, t.tDate, c.custName, t.PayableAmnt))
  			
		self.window.show_all()
		
	def on_add_clicked(self,sender):
		self.addNew()
							
	def addNew(self,transId=None):
		query   = self.session.query(Trades.Code).select_from(Trades).filter(Trades.Sell == self.sell)
		lastCode  = query.order_by(Trades.Code.desc()).first()
		if not lastCode:
			self.Code  = 1
		else:
			self.Code  = int(lastCode.Code) + 1

		self.mainDlg = self.builder.get_object("FormWindow")

		self.Codeentry = self.builder.get_object("transCode")
		self.Codeentry.set_text(LN(self.Code))
		self.statusBar  = self.builder.get_object("FormStatusBar")	
		self.tradeTreeView = self.builder.get_object("TradeTreeView")
		self.sellListStore = Gtk.TreeStore(str,str,str,str,str,str,str,str)
		self.sellListStore.clear()
		self.tradeTreeView.set_model(self.sellListStore)
		
		headers = (_("No."), _("Product Name"), _("Quantity"), _("Unit Price"), 
				   _("Total Price"), _("Unit Disc."), _("Disc."), _("Description"))
		txt = 0
		for header in headers:
			column = Gtk.TreeViewColumn(header,Gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.tradeTreeView.append_column(column)
			txt += 1
		#self.tradeTreeView.get_selection().set_mode(  Gtk.SelectionMode.SINGLE    )
		
		self.paymentManager = payments.Payments(transId=self.Id,transCode=self.Code)
		self.paymentManager.connect("payments-changed", self.setNonCashPayments)
		self.paymentManager.fillPaymentTables()

		if transId:
			sellsQuery  = self.session.query(Exchanges).select_from(Exchanges)
			sellsQuery  = sellsQuery.filter(Exchanges.exchngTransId==transId).order_by(Exchanges.exchngNo.asc()).all()
			for sell in sellsQuery:
				ttl     = sell.exchngUntPrc * sell.exchngQnty
				disc    = sell.exchngUntDisc * sell.exchngQnty
				list    = (sell.exchngNo,sell.exchngProduct,sell.exchngQnty,sell.exchngUntPrc,str(ttl),sell.exchngUntDisc,str(disc),sell.exchngDesc)
				self.sellListStore.append(None,list)
		
		
		if self.editFalg:
			self.Id	= self.editTransaction.Id
			self.Code 	= self.editTransaction.Code
		
			
			self.paymentManager = payments.Payments(transId=self.Id,transCode=self.Code)
			self.paymentManager.connect("payments-changed", self.setNonCashPayments)
			self.paymentManager.fillPaymentTables()
			print self.Id
			self.builder.get_object("fullFactorSellBtn").set_label("Save Changes ...")
			
			self.Codeentry = self.builder.get_object("transCode")
			if config.digittype == 1:
				self.Codeentry.set_text(utility.convertToPersian(str(self.editTransaction.Code)))				
			else:
				self.Codeentry.set_text(str(self.editTransaction.Code))			
						
			self.additionsEntry.set_text(str(self.editTransaction.Addition))	
			query = self.session.query(Customers).select_from(Customers)
			customer = query.filter(Customers.custId == self.editTransaction.Cust).first()						
			self.sellerSelected(self, self.editTransaction.Cust,customer.custCode)	
					
			query=self.session.query(Exchanges).select_from(Exchanges)
			exchanges = query.filter(Exchanges.exchngTransId==self.editTransaction.Id).all()			
			number=1
			for exchange in exchanges:							
				query=self.session.query(Products).select_from(Products)
				product = query.filter(Products.id==exchange.exchngProduct).first()
				sellList = (str(number), product.name, exchange.exchngQnty, exchange.exchngUntPrc,
						 exchange.exchngQnty*exchange.exchngUntPrc, exchange.exchngUntDisc,
						 float(exchange.exchngQnty)*float(exchange.exchngUntDisc), exchange.exchngDesc)
				self.sellListStore.append(None,sellList)
				self.appendPrice(exchange.exchngQnty*exchange.exchngUntPrc)
				self.appendDiscount(float(exchange.exchngQnty)*float(exchange.exchngUntDisc))
				self.valsChanged()
				number+=1																
			self.taxEntry.set_text(str(self.editTransaction.Tax))
			self.additionsEntry.set_text(str(self.editTransaction.Addition))
			self.cashPymntsEntry.set_text(str(self.editTransaction.CashPayment))
			self.builder.get_object("FOBEntry").set_text(str(self.editTransaction.Delivery))
			self.builder.get_object("shipViaEntry").set_text(str(self.editTransaction.ShipVia))
			self.builder.get_object("transDescEntry").set_text(str(self.editTransaction.Desc))
			self.factorDate.set_text(str(self.editTransaction.LastEdit))			
			self.factorDate.showDateObject(self.editTransaction.LastEdit)																											
		self.mainDlg.show_all()
																	
	def editSelling(self,transId=None):
		self.editFalg=True		
		selection = self.treeview.get_selection()
		iter = selection.get_selected()[1]		
		code = self.treestore.get_value(iter, 0) 		
		query = config.db.session.query(Trades, Customers)
		query = query.select_from(outerjoin(Trades, Customers, Trades.Cust== Customers.custId))
		result,result2 = query.filter(Trades.Id == code).first() 		
 		self.editTransaction=result 	
 		self.addNew() 		
 		
																						
	def removeSelling(self, sender):
		selection = self.treeview.get_selection()
		iter1 = selection.get_selected()[1]	
		code = self.treestore.get_value(iter1, 0)
		print code
		query = config.db.session.query(Trade).select_from(Trade)
		Transaction = query.filter(Trades.Id ==unicode(code) )
		Transaction = Transaction.filter(Trades.Acivated==1).first()
		TransactionId=Transaction.Id
		
		exchanges=self.session.query(Exchanges).select_from(Exchanges)
		exchanges=exchanges.filter(Exchanges.exchngTransId==TransactionId).all()
		
		for exchange in exchanges:
			product=self.session.query(Products).select_from(Products)
			product= product.filter(Products.id==exchange.exchngProduct).first()
			product.quantity+=exchange.exchngQnty
			
		
		
		
		query = config.db.session.query(Trade).select_from(Trade)
		Transaction = query.filter(Trades.Id ==unicode(code) ).all()
		for trans in Transaction:
			trans.Acivated=0
		config.db.session.commit()
		self.treestore.remove(iter1)	
		
		


	def selectCustomers(self,sender=0):
		customer_win = customers.Customer()
		customer_win.viewCustomers()
		code = self.customerEntry.get_text()
		if code != '':
			customer_win.highlightCust(code)
		customer_win.connect("customer-selected", self.sellerSelected)
		
	def sellerSelected(self, sender, id, code):
		self.customerEntry.set_text(code)
		sender.window.destroy()		
		self.setCustomerName()
				
	def setCustomerName(self, sender=0, ev=0):
		ccode = unicode(self.customerEntry.get_text())
		query = self.session.query(Customers).select_from(Customers)
		customer = query.filter(Customers.custId == ccode).first()
		if customer:
			self.customerNameEntry.set_text(customer.custName)
		else:
			self.customerNameEntry.set_text("")

	def selectProduct(self,sender=0):
		obj = product.Product()
		obj.viewProducts()
		obj.connect("product-selected",self.proSelected)
		code = self.proVal.get_text()
		obj.highlightProduct(unicode(code))

	def proSelected(self,sender=0, id=0, code=0):
		code = unicode(code)
		selectedPro = self.session.query(Products).select_from(Products).filter(Products.code==code).first()
		id      = selectedPro.id
		code    = selectedPro.code
		name    = selectedPro.name
		av_qnty    = selectedPro.quantity
		sellPrc = selectedPro.sellingPrice
		formula  = selectedPro.discountFormula
		
		qnty = self.qntyEntry.get_float()
		discnt = self.calcDiscount(formula, qnty, sellPrc)
		
		self.avQntyVal.set_text(utility.LN(av_qnty))
		self.stnrdDisc.set_text(utility.LN(discnt))
		self.unitPriceEntry.set_text(utility.LN(sellPrc, comma=False))
		self.discountEntry.set_text(utility.LN(discnt, comma=False))

		self.stndrdPVal.set_text(utility.LN(sellPrc))

		self.proNameLbl.show()
		
		self.avQntyVal.show()
		self.stnrdDisc.show()
		self.stndrdPVal.show()
		
		if sender:
			self.proVal.set_text(code)
			sender.window.destroy()

	def addProduct(self,sender=0,edit=None):
		self.addDlg = self.builder.get_object("addDlg")
		if edit:
			self.editCde    = edit[0]
			ttl = "Edit sell:\t%s - %s" %(self.editCde,edit[1])
			self.addDlg.set_title(ttl)
			self.edtSellFlg = True		#TODO find usage
			self.oldTtl     = utility.getFloat(edit[4])
			self.oldTtlDisc = utility.getFloat(edit[6])
			btnVal  = "Save Changes..."
		else:
			self.editingSell    = None
			self.addDlg.set_title("Choose sell information")
			self.edtSellFlg = False
			btnVal  = "Add to list"
			
		self.proVal        = self.builder.get_object("proEntry")
		self.discountEntry = self.builder.get_object("discountEntry")
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
			(No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc) = edit
			pName   = unicode(pName)
			pro = self.session.query(Products).select_from(Products).filter(Products.name==pName).first()
			self.proVal.set_text(pro.code)
			self.product_code = pro.code
			
			self.qntyEntry.set_text(qnty)
			self.quantity = utility.getFloat(qnty)
			
			self.unitPriceEntry.set_text(untPrc.replace(',', ''))
			self.discountEntry.set_text(untDisc.replace(',', ''))
			self.descVal.set_text(desc)
			
			self.proNameLbl.set_text(pName)
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
				
	def editProduct(self,sender):
		iter    = self.tradeTreeView.get_selection().get_selected()[1]
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
			edtTpl  = (No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc)
			self.addProduct(edit=edtTpl)
		
	def removeProduct(self,sender):
		delIter = self.tradeTreeView.get_selection().get_selected()[1]
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
			length  = len(self.sellsItersDict) -1
			if len(self.sellsItersDict) > 1:
				while No < length:
					print No
					nextIter    = self.sellsItersDict[No+1]
					self.sellListStore.set_value(nextIter,0,str(No))
					self.sellsItersDict[No] = nextIter
					del self.sellsItersDict[No+1]
					No  += 1
				print "--------------",length
			else:
				self.sellsItersDict = {}
				
	def upProInList(self,sender):
		if len(self.sellsItersDict) == 1:
			return
		iter    = self.tradeTreeView.get_selection().get_selected()[1]
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
		iter    = self.tradeTreeView.get_selection().get_selected()[1]
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
		product   = self.session.query(Products).select_from(Products).filter(Products.code==proCd).first()
		if not product:
			errorstr = _("The \"Product Code\" which you selected is not a valid Code.")
			msgbox = Gtk.MessageDialog( self.addDlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, 
										Gtk.ButtonsType.OK, errorstr )
			msgbox.set_title(_("Invalid Product Code"))
			msgbox.run()
			msgbox.destroy()
			return
		else:
			productName = product.name
			purchasePrc = product.purchacePrice
		qnty    = self.qntyEntry.get_float()
		over    = product.oversell
		avQnty  = product.quantity
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
			sellList    = (str(No),productName,str(qnty),str(slPrc),str(total),untDisc,discnt,descp)
			for i in range(len(sellList)):
				self.sellListStore.set(self.editingSell,i,sellList[i])
			
			self.appendPrice(total - self.oldTtl)
			self.appendDiscount(discnt_val - self.oldTtlDisc)
			self.valsChanged()
			self.sellsItersDict[No]   = self.editingSell
			self.addDlg.hide()
			
		else:
			No = len(self.sellsItersDict) + 1
			
			No_str = str(No)
			qnty_str = str(qnty)
			slPrc_str = str(slPrc)
			total_str = str(total)
			if config.digittype == 1:
				No_str = utility.convertToPersian(No_str)
				qnty_str = utility.LN(qnty_str)
				slPrc_str = utility.LN(slPrc_str)
				total_str = utility.LN(total_str)
				untDisc = utility.convertToPersian(untDisc)
				
			sellList = (No_str, productName, qnty_str, slPrc_str, total_str, untDisc, discnt, descp)
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
		zerostr = "0.0"
		if config.digittype == 1:
			zerostr = utility.convertToPersian(zerostr)
			
		self.proVal.set_text("")
		self.qntyEntry.set_text(zerostr)
		self.unitPriceEntry.set_text(zerostr)
		self.discountEntry.set_text("")
		self.proNameLbl.set_text("")
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
		ttlDiscs    = self.listTotalDiscount + utility.getFloat(self.builder.get_object("custDiscount").get_text())
		additions   = self.additionsEntry.get_float()
		subtracts   = self.subsEntry.get_float()
		taxEntry    = self.taxEntry
		feeEntry    = self.feeEntry

		self.totalDiscsEntry.set_text(utility.LN(ttlDiscs))
		self.totalFactor = subtotal + additions - subtracts - ttlDiscs
		print self.totalFactor
		if self.vatCheck:
			self.VAT = self.totalFactor * dbconf.get_int("vat-rate")/100
			self.fee = self.totalFactor * dbconf.get_int("fee-rate")/100
			self.totalTax = self.VAT + self.fee

			taxEntry.set_text(str(self.VAT))
			feeEntry.set_text(str(self.fee))
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
		if self.product_code != productCd:
			print "validateCode"
			product = self.session.query(Products).select_from(Products).filter(Products.code==productCd).first()
			if not product:
				self.proVal.modify_base(Gtk.StateType.NORMAL,self.redClr)
				msg = "Product code is invalid"
				self.proVal.set_tooltip_text(msg)
				self.addStBar.push(1,msg)
				self.proNameLbl.set_text("")
				self.product = None
			else:
				self.proVal.modify_base(Gtk.StateType.NORMAL,self.whiteClr)
				self.proVal.set_tooltip_text("")
				self.proSelected(code=product.code)
				self.proNameLbl.set_text(str(product.name))
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
				print "validateQnty"
				qntyAvlble  = float(self.product.quantity)
				over    = self.product.oversell
				if qnty < 0:
					self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					if not stMsg:
						stMsg  = "Quantity must be greater than 0."
						severe = True
					self.qntyEntry.set_tooltip_text("Quantity must be greater than 0.")

				elif qnty > qntyAvlble and not over:
					self.qntyEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					msg = "Quantity is more than the available storage. (Over-Sell is Off)"
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
						print "formula exists!"
						discval = self.calcDiscount(self.product.discountFormula, qnty, sellPrc)
						discstr = utility.LN(discval)
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
					erMsg  = "Unit Price cannot be negative."
					self.unitPriceEntry.set_tooltip_text(erMsg)
					if not stMsg:
						stMsg   = erMsg
						severe = True

				elif untPrc < purcPrc:
					self.unitPriceEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					err  = "Unit Price is less than the product purchase price."
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
		print "validateDiscnt"
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
					print disc
					pindex = disc.find(u'%')
					if pindex == 0 or pindex == len(disc) - 1:
						discp = float(disc.strip(u'%'))
						
						if discp > 100 or discp < 0:
							self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
							errMess  = "Invalid discount range. (Discount must be between 0 and 100 percent)"
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
							errMess  = "Invalid discount. (Use numbers and percentage sign only)"
							self.discountEntry.set_tooltip_text(errMess)
					else:
						self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
						errMess  = "Invalid discount. (Put percentage sign before or after discount amount)"
						self.discountEntry.set_tooltip_text(errMess)
						if not stMsg:
							stMsg  = errMess
							severe = True
				
			
			self.addStBar.push(1,stMsg)
			if not severe:
				if untPrc - discval < purcPrc:
					self.discountEntry.modify_base(Gtk.StateType.NORMAL,self.redClr)
					errMess  = "Applying discount decreases product price below its purchase price!"
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
						continue
					elif qnty == firstnum:
						discnt = sell_price - float(partlist[1])
						break
					else:
						break
				elif len(numlist) == 2:
					firstnum = float(numlist[0])
					secnum = float(numlist[1])
					if qnty > secnum:
						continue
					elif qnty < firstnum:
						break
					else:
						discnt = sell_price - float(partlist[1])
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
			self.registerExchanges()			
			if not self.subPreInv:
				self.registerDocument()			
			self.mainDlg.hide()						
				
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
			self.statusBar.push(1, "There is no product selected for the invoice.")
			return False
						
		self.subCode    = self.Code
		
		self.subDate    = self.factorDate.getDateObject()
		self.subPreInv  = self.builder.get_object("preChkBx").get_active()
		
		if not self.subPreInv:
			pro_dic = {}
			for exch in self.sellListStore:
				pro_name = unicode(exch[1])
				pro_qnty = utility.getFloat(exch[2])
				
				if pro_name in pro_dic:
					pro_dic[pro_name] -= pro_qnty
				else:
					query   = self.session.query(Products).select_from(Products).filter(Products.name == pro_name)
					pro = query.first()
					if not pro.oversell:
						pro_dic[pro_name] = pro.quantity - pro_qnty
			
			pro_str = ""
			for (k, v) in pro_dic.items():
				print "%s : %d" % (k, v)
				if v < 0:
					pro_str += k + _(", ")
					
			pro_str.strip()
			print pro_str
			
			if pro_str:
				msg = _("The available quantity of %s is not enough for the invoice. You can save it as pre-invoice.") \
						% pro_str
				self.statusBar.push(1, msg)
				return False
									
		self.subAdd     	= self.additionsEntry.get_float()
		self.subSub     	= self.subsEntry.get_float()
		self.subShpDate 	= self.shippedDate.getDateObject()
		self.subFOB     	= unicode(self.builder.get_object("FOBEntry").get_text())
		self.subShipVia 	= unicode(self.builder.get_object("shipViaEntry").get_text())
		self.subDesc    	= unicode(self.builder.get_object("transDescEntry").get_text())
	#	self.editdate		=self.
		self.totalFactor 	= utility.getFloat(self.payableAmntEntry.get_text())
		self.totalDisc 		= utility.getFloat(self.totalDiscsEntry.get_text())
		self.totalPayment 	= utility.getFloat(self.totalPaymentsEntry.get_text())
		self.statusBar.push(1,"")
		return True

	def registerTransaction(self):
		if self.editFalg:
			query=self.session.query(Trade).select_from(Trade)
			query=query.filter(Trades.Code==self.subCode).all()
			for trans in query:
				trans.Acivated=0
			sell = Trade( self.subCode, self.subDate, 0, self.custId, self.subAdd, self.subSub, self.VAT, self.fee, self.totalFactor, self.cashPayment,
								self.subShpDate, self.subFOB, self.subShipVia, self.subPreInv, self.subDesc, self.sell, self.editDate, 1)

		else:
			sell = Trades(self.subCode, self.subDate, 0, self.custId, self.subAdd, self.subSub, self.VAT, self.fee, self.totalFactor, self.cashPayment,
					self.subShpDate, self.subFOB, self.subShipVia, self.subPreInv, self.subDesc, self.sell, self.subDate, 1)#editdate=subdate

		self.session.add(sell)
		self.session.commit()

		self.treestore.append(None,(int(self.Id), LN(self.subCode), str(self.subDate), "test", str(self.totalFactor)))
		
	def registerExchanges(self):	
				
		# Exchanges( self, exchngNo, exchngProduct, exchngQnty,
		#            exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc):
		if self.editFalg:								
			#get last trans id beacause in the save transaction we save this transaction
			lasttransId=self.session.query(Trade).select_from(Trade)
			lasttransId=lasttransId.order_by(Trades.Id.desc())				
			lasttransId=lasttransId.filter(Trades.Code==self.Code)
			lasttransId=lasttransId.filter(Trades.Id!=self.Id).first()
			lasttransId1=lasttransId.Id
			
			lasttransId=self.session.query(Trade).select_from(Trade)
			lasttransId=lasttransId.order_by(Trades.Id.desc())				
			lasttransId=lasttransId.filter(Trades.Code==self.Code)
			lasttransId=lasttransId.filter(Trades.Id!=lasttransId1).first()
			lasttransId=lasttransId.Id											
			
			exchange1 =self.session.query(Exchanges).select_from(Exchanges)
			exchange1=exchange1.order_by(Exchanges.exchngTransId.desc())
			exchange1=exchange1.filter(Exchanges.exchngTransId==lasttransId)
			
			for exchange in exchange1:
				query   = self.session.query(Products).select_from(Products).filter(Products.id == exchange.exchngProduct)
				pro = query.first()
				pro.quantity+=exchange.exchngQnty
			self.session.commit()			
		for exch in self.sellListStore:
			query = self.session.query(Products).select_from(Products)
			pid = query.filter(Products.name == unicode(exch[1])).first().id
						
			self.lastexchangequantity=utility.getFloat(0)
			self.nowexchangequantity=utility.getFloat(exch[2])
						
			if self.editFalg:
											
				#get last trans id beacause in the save transaction we save this transaction
				lasttransId=self.session.query(Trade).select_from(Trade)
				lasttransId=lasttransId.order_by(Trades.Id.desc())				
				lasttransId=lasttransId.filter(Trades.Code==self.Code)
				lasttransId=lasttransId.filter(Trades.Id!=self.Id).first()
				lasttransId1=lasttransId.Id
				
				lasttransId=self.session.query(Trade).select_from(Trade)
				lasttransId=lasttransId.order_by(Trades.Id.desc())				
				lasttransId=lasttransId.filter(Trades.Code==self.Code)
				lasttransId=lasttransId.filter(Trades.Id!=lasttransId1).first()
				lasttransId=lasttransId.Id											
								
				exchange1 =self.session.query(Exchanges).select_from(Exchanges)
				exchange1=exchange1.order_by(Exchanges.exchngTransId.desc())
				exchange1=exchange1.filter(Exchanges.exchngProduct==pid)
				exchange1=exchange1.filter(Exchanges.exchngTransId==lasttransId).first()
				
				if not exchange1:					
					self.lastexchangequantity=utility.getFloat(str(0))
					self.nowexchangequantity=utility.getFloat(exch[2])
					
					exchange = Exchanges(utility.getInt(exch[0]), pid, utility.getFloat(exch[2]),
										 utility.getFloat(exch[3]), utility.convertToLatin(exch[5]),
										 lasttransId1, unicode(exch[7]))
					self.session.add( exchange )
					self.session.commit()										
				else:
					self.lastexchangequantity=utility.getFloat(str(exchange1.exchngQnty))
					self.nowexchangequantity=utility.getFloat(exch[2])
										
					exchange = Exchanges(utility.getInt(exch[0]), pid, utility.getFloat(exch[2]),
										 utility.getFloat(exch[3]), utility.convertToLatin(exch[5]),
										 lasttransId1, unicode(exch[7]))
					self.session.add( exchange )
					self.session.commit()
					
			# in add mode transaction																						
			else:	
				self.lastexchangequantity=utility.getFloat(str(0))
				self.nowexchangequantity=utility.getFloat(exch[2])
				exchange = Exchanges(utility.getInt(exch[0]), pid, utility.getFloat(exch[2]),
									 utility.getFloat(exch[3]), utility.convertToLatin(exch[5]),
									 self.Id, unicode(exch[7]))
				self.session.add( exchange )									
							
			#---- Updating the products quantity
			#TODO product quantity should be updated while adding products to factor
			if not self.subPreInv:
					query   = self.session.query(Products).select_from(Products).filter(Products.id == pid)
					pro = query.first()									

					pro.quantity -= self.nowexchangequantity
					
					self.lastexchangequantity=utility.getFloat(0)
					self.nowexchangequantity=utility.getFloat(0)
					self.session.commit()
					
		
	def registerDocument(self):
		# dbconf = dbconfig.dbConfig()		
		query = self.session.query(Cheque).select_from(Cheque)
		cheques = query.filter(Cheque.chqTransId == self.Id).all()

		cust_code = unicode(self.customerEntry.get_text())
		query = self.session.query(Customers).select_from(Customers)
		cust = query.filter(Customers.custCode == cust_code).first()
			
		for pay in cheques:	
			print pay.chqId
			print pay.chqCust
			pay.chqCust=cust.custId
			print cust.custId
			self.session.add(pay)
			self.session.commit()

		# Create new document
		bill_id = self.saveDocument();
		
		# Assign document to the current transaction
		query = self.session.query(Trades)#.select_from(Trade)
		query = query.filter(Trades.Id == self.Code)
		query.update( {Trades.Bill : bill_id } )	
		self.session.commit()	
	
		query = self.session.query(Cheque)#.select_from(Cheque)
		query = query.filter(Cheque.chqTransId == self.Id)
		query.update( {Cheque.chqBillId : bill_id } )
 		self.session.commit()
 		
 		
		query = self.session.query(Payment)#.select_from(Payment)
		query = query.filter(Payment.paymntTransId == self.Code)
		query =query.update( {Payment.paymntBillId : bill_id } )		
 		self.session.commit()
 			
	
# 	def RegisterBill(self):
# 		print'test'

	def printTransaction(self,sender=0):
		print "main page \"PRINT button\" is pressed!", sender
	
	def setNonCashPayments(self, sender, str_value):
		self.nonCashPymntsEntry.set_text(str_value)

	def close(self, sender=0):

		print 'closing selling form'
		print self.Id
		if self.editFalg==False:			
			query = self.session.query(Payment).select_from(Payment)
			query = query.filter(Payment.paymntTransId == self.Id)			
			payment = query.all()				
			for pay in payment:	
				self.session.delete(pay)
			self.session.commit()
			
			query = self.session.query(Cheque).select_from(Cheque)
			query = query.filter(Cheque.chqTransId == self.Id)			
			cheque = query.all()				
			for pay in cheque:	
				self.session.delete(pay)
			self.session.commit()
				
		self.mainDlg.hide_all()
		return True;

	def saveDocument(self):
		dbconf = dbconfig.dbConfig()
		# total = self.payableAmnt - self.totalDisc + self.subAdd + self.subTax
		
		trans_code = utility.LN(self.subCode, False)
		if self.sell:
			self.Document.add_notebook(self.custSubj, -(self.totalFactor), _("Debit for invoice number %s") % trans_code)
			if self.cashPayment:
				self.Document.add_notebook(self.custSubj, self.cashPayment, _("Cash Payment for invoice number %s") % trans_code)
				self.Document.add_notebook(dbconf.get_int("cash"), -(self.cashPayment), _("Cash Payment for invoice number %s") % trans_code)
			if self.totalDisc:
				self.Document.add_notebook(dbconf.get_int("sell-discount"), -(self.totalDisc), _("Discount for invoice number %s") % trans_code)
			if self.subAdd:
				self.Document.add_notebook(dbconf.get_int("sell-adds"), self.subAdd, _("Additions for invoice number %s") % trans_code)
			if self.VAT:
				self.Document.add_notebook(dbconf.get_int("sell-vat"), (self.VAT), _("VAT for invoice number %s") % trans_code)
			if self.fee:
				self.Document.add_notebook(dbconf.get_int("sell-fee"), (self.fee), _("Fee for invoice number %s") % trans_code)
		else:
			self.Document.add_notebook(self.custSubj, self.totalFactor, _("Debit for invoice number %s") % trans_code)
			if self.cashPayment:
				self.Document.add_notebook(self.custSubj, -(self.cashPayment), _("Cash Payment for invoice number %s") % trans_code)
				self.Document.add_notebook(dbconf.get_int("cash"), self.cashPayment, _("Cash Payment for invoice number %s") % trans_code)
			if self.totalDisc:
				self.Document.add_notebook(dbconf.get_int("buy-discount"), self.totalDisc, _("Discount for invoice number %s") % trans_code)
			if self.subAdd:
				self.Document.add_notebook(dbconf.get_int("buy-adds"), -self.subAdd, _("Additions for invoice number %s") % trans_code)
			if self.VAT:
				self.Document.add_notebook(dbconf.get_int("buy-vat"), -(self.VAT), _("VAT for invoice number %s") % trans_code)
			if self.fee:
				self.Document.add_notebook(dbconf.get_int("buy-fee"), -(self.fee), _("Fee for invoice number %s") % trans_code)
  		
		# Create a row for each sold product
		for exch in self.sellListStore:
			query = self.session.query(ProductGroups.sellId)
			query = query.select_from(outerjoin(Products, ProductGroups, Products.accGroup == ProductGroups.id))
			result = query.filter(Products.name == unicode(exch[1])).first()
			sellid = result[0]

			exch_totalAmnt = utility.getFloat(exch[2]) * utility.getFloat(exch[3])
			#TODO Use unit name specified for each product
			if self.sell:
				self.Document.add_notebook(sellid, exch_totalAmnt, _("Selling %s units, invoice number %s") % (exch[2], trans_code))
  			else:
				self.Document.add_notebook(sellid, -exch_totalAmnt, _("Buying %s units, invoice number %s") % (exch[2], trans_code))

# 		# Create rows for payments
# 		row = Notebook(self.custSubj, bill.id, self.totalPayment, 
# 		               _("Payment for invoice number %s") % trans_code)
# 		self.session.add(row)
# 		# doc_rows.append(row)
# 		row = Notebook(dbconf.get_int("fund"), bill.id, -(self.cashPayment), 
# 		               _("Cash Payment for invoice number %s") % trans_code)
# 		self.session.add(row)
# 		# doc_rows.append(row)
# 		row = Notebook(dbconf.get_int("acc-receivable"), bill.id, -(self.totalPayment - self.cashPayment),
# 		               _("Non-cash Payment for invoice number %s") % trans_code)
# 		self.session.add(row)
# 		# doc_rows.append(row)
  		
# 		#TODO Add rows for customer introducer's commision
  		
# 		# self.session.add_all(doc_rows)
# 		self.session.commit()
		docnum = self.Document.save()
		share.mainwin.silent_daialog(_("Document saved with number %s.") % docnum)

	def vatCalc(self, sender=0, ev=0):
		self.vatCheck = self.builder.get_object("vatCheck").get_active()
		if not self.vatCheck:
			self.builder.get_object("taxEntry").set_text("0")
			self.builder.get_object("feeEntry").set_text("0")

		self.builder.get_object("taxEntry").set_sensitive(self.vatCheck)
		self.builder.get_object("feeEntry").set_sensitive(self.vatCheck)

		self.valsChanged()
## @}
