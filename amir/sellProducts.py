import sys
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

import  gobject
import  pygtk
import  gtk

from    sqlalchemy.orm              import  sessionmaker, join
from    helpers                     import  get_builder
from    sqlalchemy.orm.util         import  outerjoin
from    amirconfig                  import  config
from    datetime                    import  date
from    sqlalchemy.sql              import  and_
from    sqlalchemy.sql.functions    import  *
from    database                    import  *

pygtk.require('2.0')

class SellProducts:
	def __init__(self,transId=None):
		self.builder    = get_builder("SellingForm")
		self.session    = config.db.session
		
		self.sellsItersDict  = {}
		self.paysItersDict   = {}

		self.redClr = gtk.gdk.color_parse("#FFCCCC")
		self.whiteClr = gtk.gdk.color_parse("#FFFFFF")
		
		query   = self.session.query(Transactions.transId).select_from(Transactions)
		lastId  = query.order_by(Transactions.transId.desc()).first()
		if not lastId:
			lastId  = 0
		else:
			lastId  = lastId.transId
		self.transId = lastId + 1
		
		self.mainDlg = self.builder.get_object("sellFormWindow")
		self.transCode = self.builder.get_object("transCode")
		if config.digittype == 1:
			self.transCode.set_text(utility.convertToPersian(str(self.transId)))
		else:
			self.transCode.set_text(str(self.transId))
		
		self.factorDate = DateEntry()
		self.builder.get_object("datebox").add(self.factorDate)
		self.factorDate.show()
		
		self.shippedDate = DateEntry()
		self.builder.get_object("shippedDateBox").add(self.shippedDate)
		self.shippedDate.show()
		
		self.additionsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("additionsbox").add(self.additionsEntry)
		self.additionsEntry.set_alignment(0.95)
		self.additionsEntry.show()
		self.additionsEntry.connect("changed", self.valsChanged)
		
		self.subsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("subsbox").add(self.subsEntry)
		self.subsEntry.set_alignment(0.95)
		self.subsEntry.show()
		self.subsEntry.connect("changed", self.valsChanged)
		
		self.cashPymntsEntry = decimalentry.DecimalEntry()
		self.builder.get_object("cashbox").add(self.cashPymntsEntry)
		self.cashPymntsEntry.set_alignment(0.95)
		self.cashPymntsEntry.show()
		self.cashPymntsEntry.connect("changed", self.paymentsChanged)
		
		self.qntyEntry = decimalentry.DecimalEntry()
		self.builder.get_object("qntyBox").add(self.qntyEntry)
		self.qntyEntry.show()
		self.qntyEntry.connect("focus-out-event", self.validateQnty)
		
		self.unitPriceEntry = decimalentry.DecimalEntry()
		self.builder.get_object("unitPriceBox").add(self.unitPriceEntry)
		self.unitPriceEntry.show()
		self.unitPriceEntry.connect("focus-out-event", self.validatePrice)
		
		self.customerEntry        = self.builder.get_object("sellerCodeEntry")
		self.totalEntry         = self.builder.get_object("subtotalEntry")
		self.totalDiscsEntry    = self.builder.get_object("totalDiscsEntry")
		self.payableAmntEntry   = self.builder.get_object("payableAmntEntry")
		self.totalPaymentsEntry = self.builder.get_object("totalPaymentsEntry")
		self.remainedAmountEntry= self.builder.get_object("remainedAmountEntry")
		self.nonCashPymntsEntry = self.builder.get_object("nonCashPymntsEntry")
		self.buyerNameEntry     = self.builder.get_object("buyerNameEntry")
		self.taxEntry           = self.builder.get_object("taxEntry")

		self.statusBar  = self.builder.get_object("sellFormStatusBar")
		
		self.sellsTreeView = self.builder.get_object("sellsTreeView")
		self.sellListStore = gtk.TreeStore(str,str,str,str,str,str,str,str)
		self.sellListStore.clear()
		self.sellsTreeView.set_model(self.sellListStore)
		
		headers = (_("No."), _("Product Name"), _("Quantity"), _("Unit Price"), 
				   _("Total Price"), _("Unit Disc."), _("Disc."), _("Description"))
		txt = 0
		for header in headers:
			column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
			column.set_spacing(5)
			column.set_resizable(True)
			self.sellsTreeView.append_column(column)
			txt += 1
		self.sellsTreeView.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
		
		self.paymentManager = payments.Payments(transId=self.transId)
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
				print "---------------------------------"
		
		self.builder.connect_signals(self)
		self.mainDlg.show_all()

	def appendPrice(self,  price):
		oldPrice    = utility.getFloatNumber(self.totalEntry.get_text())
		totalPrce   = oldPrice + price
		self.totalEntry.set_text(utility.showNumber(totalPrce))

	def appendDiscount(self, discount):
		oldDiscount = utility.getFloatNumber(self.totalDiscsEntry.get_text())
		oldDiscount = oldDiscount + float(discount) 
		self.totalDiscsEntry.set_text(utility.showNumber(oldDiscount))
		
	def editSell(self,sender):
		iter    = self.sellsTreeView.get_selection().get_selected()[1]
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
			self.addSell(edit=edtTpl)
		
	def removeSell(self,sender):
		delIter = self.sellsTreeView.get_selection().get_selected()[1]
		if delIter:
			No  = int(self.sellListStore.get(delIter, 0)[0])
			msg = _("Are You sure you want to delete the sell row number %s?") %No
			msgBox  = gtk.MessageDialog( self.mainDlg, gtk.DIALOG_MODAL,
											gtk.MESSAGE_QUESTION,
											gtk.BUTTONS_OK_CANCEL, msg         )
			msgBox.set_title(            _("Confirm Deletion")              )
			answer  = msgBox.run(                                           )
			msgBox.destroy(                                                 )
			if answer != gtk.RESPONSE_OK:
				return
			ttlPrc  = float(self.sellListStore.get(delIter,4)[0])
			ttlDisc = float(self.sellListStore.get(delIter,6)[0])
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
				
	def reducePrice(self,  price):
		oldPrice    = utility.getFloatNumber(self.totalEntry.get_text())
		totalPrce   = oldPrice - price
		self.totalEntry.set_text(utility.showNumber(totalPrce))

	def reduceDiscount(self, discount):
		oldDiscount = utility.getFloatNumber(self.totalDiscsEntry.get_text())
		oldDiscount = oldDiscount - discount
		self.totalDiscsEntry.set_text(utility.showNumber(oldDiscount))

	def addSell(self,sender=0,edit=None):
		self.addSellDlg = self.builder.get_object("addASellDlg")
		if edit:
			self.editCde    = edit[0]
			ttl = "Edit sell:\t%s - %s" %(self.editCde,edit[1])
			self.addSellDlg.set_title(ttl)
			self.edtSellFlg = True		#TODO find usage
			self.oldTtl     = utility.getFloatNumber(edit[4])
			self.oldTtlDisc = utility.getFloatNumber(edit[6])
			btnVal  = "Save Changes..."
		else:
			self.editingSell    = None
			self.addSellDlg.set_title("Choose sell information")
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
		self.addSellStBar   = self.builder.get_object("addSellStatusBar")
		self.addSellStBar.push(1,"")
		
		self.proVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		self.qntyEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		self.unitPriceEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		self.discountEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
		
		if self.edtSellFlg:
			(No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc) = edit
			pName   = unicode(pName)
			pro = self.session.query(Products).select_from(Products).filter(Products.name==pName).first()
			self.proVal.set_text(pro.code)
			self.product_code = pro.code
			
			self.qntyEntry.set_text(qnty)
			self.quantity = utility.getFloatNumber(qnty)
			
			self.unitPriceEntry.set_text(untPrc.replace(',', ''))
			self.discountEntry.set_text(untDisc.replace(',', ''))
			self.descVal.set_text(desc)
			
			self.proNameLbl.set_text(pName)
			self.avQntyVal.set_text(utility.showNumber(pro.quantity))
			self.stndrdPVal.set_text(utility.showNumber(pro.sellingPrice))
			
			self.ttlAmntVal.set_text(ttlPrc)
			self.discTtlVal.set_text(ttlDisc)
			total_payable = utility.getFloatNumber(ttlPrc) - utility.getFloatNumber(ttlDisc)
			discval = self.calcDiscount(pro.discountFormula, utility.getFloatNumber(qnty), 
										pro.sellingPrice)
			self.ttlPyblVal.set_text(utility.showNumber(total_payable))
			self.stnrdDisc.set_text(utility.showNumber(discval))
			self.product = pro
			
		else:
			self.clearSellFields()
			self.product_code = ""
			self.quantity = 0
			
		self.addSellDlg.show_all()
				
	def cancelSell(self,sender=0,ev=0):
		self.clearSellFields()
		self.addSellDlg.hide_all()
		return True

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
		
	def addSellToList(self,sender=0):
		proCd   = self.proVal.get_text()
		product   = self.session.query(Products).select_from(Products).filter(Products.code==proCd).first()
		if not product:
			errorstr = _("The \"Product Code\" which you selected is not a valid Code.")
			msgbox = gtk.MessageDialog( self.addSellDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
										gtk.BUTTONS_OK, errorstr )
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
			msgbox = gtk.MessageDialog( self.addSellDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
										gtk.BUTTONS_OK, errorstr )
			msgbox.set_title(_("Invalid Quantity"))
			msgbox.run()
			msgbox.destroy()
			return
		elif qnty > avQnty:
			if not over:
				errorstr = _("The \"Quantity\" is larger than the storage, and over-sell is off!")
				errorstr += _("\nQuantity can be at most %s.") %avQnty
				msgbox = gtk.MessageDialog( self.addSellDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
											gtk.BUTTONS_OK, errorstr )
				msgbox.set_title(_("Invalid Quantity"))
				msgbox.run()
				msgbox.destroy()
				
		slPrc   = self.unitPriceEntry.get_float()
		if slPrc <= 0:
			errorstr = _("The \"Unit Price\" Must be greater than 0.")
			msgbox = gtk.MessageDialog( self.addSellDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, 
										gtk.BUTTONS_OK, errorstr )
			msgbox.set_title(_("Invalid Unit Price"))
			msgbox.run()
			msgbox.destroy()
			return
			
		if slPrc < purchasePrc:
			msg     = _("The Unit Sell Price you entered is less than the product Purchase Price!\"")
			msgBox  = gtk.MessageDialog( self.addSellDlg, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
											gtk.BUTTONS_OK_CANCEL, msg                             )
			msgBox.set_title(               _("Are you sure?")              )
			answer  = msgBox.run(                                           )
			msgBox.destroy(                                                 )
			if answer != gtk.RESPONSE_OK:
				return

				
		headers = ("Code","Product Name","Quantity","Unit Price","Unit Discount","Discount","Total Price","Description")
		#----values:
		discnt  = self.discTtlVal.get_text()
		discnt_val = utility.getFloatNumber(discnt)
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
			self.addSellDlg.hide()
			
		else:
			No = len(self.sellsItersDict) + 1
			
			No_str = str(No)
			qnty_str = str(qnty)
			slPrc_str = str(slPrc)
			total_str = str(total)
			if config.digittype == 1:
				No_str = utility.convertToPersian(No_str)
				qnty_str = utility.showNumber(qnty_str)
				slPrc_str = utility.showNumber(slPrc_str)
				total_str = utility.showNumber(total_str)
				untDisc = utility.convertToPersian(untDisc)
				
			sellList = (No_str, productName, qnty_str, slPrc_str, total_str, untDisc, discnt, descp)
			iter = self.sellListStore.append(None, sellList)
			self.appendPrice(total)
			self.appendDiscount(discnt_val)
			self.valsChanged()
			self.sellsItersDict[No]   = iter
			self.addSellDlg.hide()

	def upSellInList(self,sender):
		if len(self.sellsItersDict) == 1:
			return
		iter    = self.sellsTreeView.get_selection().get_selected()[1]
		if iter:
			No   = int(self.sellListStore.get(iter, 0)[0])
			abvNo   = No - 1
			if abvNo > 0:
				aboveIter   = self.sellsItersDict[abvNo]
				self.sellListStore.move_before(iter,aboveIter)
				self.sellsItersDict[abvNo]  = iter
				self.sellsItersDict[No]     = aboveIter
				self.sellListStore.set_value(iter,0,str(abvNo))
				self.sellListStore.set_value(aboveIter,0,str(No))

	def downSellInList(self,sender):
		if len(self.sellsItersDict) == 1:
			return
		iter    = self.sellsTreeView.get_selection().get_selected()[1]
		if iter:
			No   = int(self.sellListStore.get(iter, 0)[0])
			blwNo   = No + 1
			if No < len(self.sellsItersDict):
				belowIter   = self.sellsItersDict[blwNo]
				self.sellListStore.move_after(iter,belowIter)
				self.sellsItersDict[blwNo]  = iter
				self.sellsItersDict[No]     = belowIter
				self.sellListStore.set_value(iter,0,str(blwNo))
				self.sellListStore.set_value(belowIter,0,str(No))
		
	def calculatePayable(self):
		subtotal    = utility.getFloatNumber(
							self.builder.get_object("subtotalEntry").get_text())
		ttlDiscs    = utility.getFloatNumber(
							self.builder.get_object("totalDiscsEntry").get_text())
		additions   = self.additionsEntry.get_float()
		subtracts   = self.subsEntry.get_float()
		
		taxEntry    = self.taxEntry
		err = False
		try:
			tax   = float(taxEntry.get_text())
			taxEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
			taxEntry.set_tooltip_text("")
		except:
			taxEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
			taxEntry.set_tooltip_text("Invalid Number")
			err     = True

		if not err:
			amnt = subtotal + additions + tax - subtracts - ttlDiscs
			self.payableAmntEntry.set_text(utility.showNumber(amnt))

	def calculateBalance(self):
		payableAmnt = utility.getFloatNumber(self.payableAmntEntry.get_text())
		ttlPayment = utility.getFloatNumber(self.totalPaymentsEntry.get_text())
		blnc = payableAmnt - ttlPayment
		self.remainedAmountEntry.set_text(utility.showNumber(blnc))
		
	
	def valsChanged(self,sender=0,ev=0):
		self.calculatePayable()
		self.calculateBalance()

	def validatePCode(self, sender, event):
		productCd   = self.proVal.get_text()
		if self.product_code != productCd:
			print "validateCode"
			product = self.session.query(Products).select_from(Products).filter(Products.code==productCd).first()
			if not product:
				self.proVal.modify_base(gtk.STATE_NORMAL,self.redClr)
				msg = "Product code is invalid"
				self.proVal.set_tooltip_text(msg)
				self.addSellStBar.push(1,msg)
				self.proNameLbl.set_text("")
				self.product = None
			else:
				self.proVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
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
				self.qntyEntry.set_text(utility.showNumber(0.0))
				qnty = 0
			else:
				qnty = self.qntyEntry.get_float()

			if self.quantity != qnty:
				print "validateQnty"
				qntyAvlble  = float(self.product.quantity)
				over    = self.product.oversell
				if qnty < 0:
					self.qntyEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
					if not stMsg:
						stMsg  = "Quantity must be greater than 0."
						severe = True
					self.qntyEntry.set_tooltip_text("Quantity must be greater than 0.")

				elif qnty > qntyAvlble and not over:
					self.qntyEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
					msg = "Quantity is more than the available storage. (Over-Sell is Off)"
					if not stMsg:
						stMsg  = msg
						severe = False
					self.qntyEntry.set_tooltip_text(msg)

				else:
					self.qntyEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
					self.qntyEntry.set_tooltip_text("")
					
				self.addSellStBar.push(1,stMsg)
				
				if not severe:
					code   = self.proVal.get_text()
					sellPrc = self.product.sellingPrice
					if self.product.discountFormula:
						print "formula exists!"
						discval = self.calcDiscount(self.product.discountFormula, qnty, sellPrc)
						discstr = utility.showNumber(discval)
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
				self.unitPriceEntry.set_text(utility.showNumber(untPrc, comma=False))
			else:
				untPrc  = self.unitPriceEntry.get_float()            
			
			if untPrc != None:
				purcPrc = self.product.purchacePrice
				if untPrc < 0:
					self.unitPriceEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
					erMsg  = "Unit Price cannot be negative."
					self.unitPriceEntry.set_tooltip_text(erMsg)
					if not stMsg:
						stMsg   = erMsg
						severe = True

				elif untPrc < purcPrc:
					self.unitPriceEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
					err  = "Unit Price is less than the product purchase price."
					self.unitPriceEntry.set_tooltip_text(err)
					if not stMsg:
						stMsg  = err

				else:
					self.unitPriceEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
					self.unitPriceEntry.set_tooltip_text("")
					
			self.addSellStBar.push(1,stMsg)
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
				discval = utility.getFloatNumber(self.stnrdDisc.get_text())
			else:
				disc  = utility.convertToLatin(self.discountEntry.get_text())
				discval = 0

				if disc != "":
					print disc
					pindex = disc.find(u'%')
					if pindex == 0 or pindex == len(disc) - 1:
						discp = float(disc.strip(u'%'))
						
						if discp > 100 or discp < 0:
							self.discountEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
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
							self.discountEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
							errMess  = "Invalid discount. (Use numbers and percentage sign only)"
							self.discountEntry.set_tooltip_text(errMess)
					else:
						self.discountEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
						errMess  = "Invalid discount. (Put percentage sign before or after discount amount)"
						self.discountEntry.set_tooltip_text(errMess)
						if not stMsg:
							stMsg  = errMess
							severe = True
				
			
			self.addSellStBar.push(1,stMsg)
			if not severe:
				if untPrc - discval < purcPrc:
					self.discountEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
					errMess  = "Applying discount decreases product price below its purchase price!"
					self.discountEntry.set_tooltip_text(errMess)
					if not stMsg:
						self.addSellStBar.push(1,errMess)
				else:
					self.discountEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
					self.discountEntry.set_tooltip_text("")
						
				self.calcTotalDiscount(discval)

	def proSelected(self,sender=0, id=0, code=0):
		print "pro selected"
		selectedPro = self.session.query(Products).select_from(Products).filter(Products.code==code).first()
		id      = selectedPro.id
		code    = selectedPro.code
		name    = selectedPro.name
		av_qnty    = selectedPro.quantity
		sellPrc = selectedPro.sellingPrice
		formula  = selectedPro.discountFormula
		
		qnty = self.qntyEntry.get_float()
		discnt = self.calcDiscount(formula, qnty, sellPrc)
		
		self.avQntyVal.set_text(utility.showNumber(av_qnty))
		self.stnrdDisc.set_text(utility.showNumber(discnt))
		self.unitPriceEntry.set_text(utility.showNumber(sellPrc, comma=False))
		self.discountEntry.set_text(utility.showNumber(discnt, comma=False))

		self.stndrdPVal.set_text(utility.showNumber(sellPrc))

		self.proNameLbl.show()
		
		self.avQntyVal.show()
		self.stnrdDisc.show()
		self.stndrdPVal.show()
		
		if sender:
			self.proVal.set_text(code)
			sender.window.destroy()

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
		self.ttlAmntVal.set_text(utility.showNumber(total))
		self.calcTotalPayable()

	def calcTotalDiscount(self, discount):
		qnty        = self.qntyEntry.get_float()
		totalDisc   = discount * qnty
		self.discTtlVal.set_text(utility.showNumber(totalDisc))
		self.calcTotalPayable()

	def calcTotalPayable(self):
		ttlAmnt = utility.getFloatNumber(self.ttlAmntVal.get_text())
		ttldiscount = utility.getFloatNumber(self.discTtlVal.get_text())
		self.ttlPyblVal.set_text(utility.showNumber(ttlAmnt - ttldiscount))

	def selectProduct(self,sender=0):
		obj = product.Product()
		obj.viewProducts()
		obj.connect("product-selected",self.proSelected)
		code = self.proVal.get_text()
		obj.highlightProduct(unicode(code))

	def close(self, sender=0):
		self.mainDlg.destroy()

	def selectSeller(self,sender=0):
		customer_win = customers.Customer()
		customer_win.viewCustomers()
		code = self.customerEntry.get_text()
		if code != '':
			customer_win.highlightCust(code)
		customer_win.connect("customer-selected",self.sellerSelected)
		
	def sellerSelected(self, sender, id, code):
		self.customerEntry.set_text(code)
		sender.window.destroy()
		
		query = self.session.query(Customers).select_from(Customers)
		customer = query.filter(Customers.custId == id).first()
		self.buyerNameEntry.set_text(customer.custName)

	def setSellerName(self,sender=0,ev=0):
		payer   = self.customerEntry.get_text()
		query   = self.session.query(Subject).select_from(Subject)
		query   = query.filter(Subject.code==payer).first()
		if not query:
			self.buyerNameEntry.set_text("")
		else:
			self.buyerNameEntry.set_text(query.name)

	def submitFactorPressed(self,sender):
		permit  = self.checkFullFactor()
		sell_factor = True
		if permit:
			print "--------- Starting... ------------"
			print "\nSaving the Transaction ----------"
			sell = Transactions( self.subCode, self.subDate, 0, self.custId, self.subAdd,
								self.subSub, self.subTax, self.cashPayment, 
								self.subShpDate, self.subFOB, self.subShipVia,
								self.subPreInv, self.subDesc, sell_factor)
			self.session.add( sell )
			self.session.commit()
			print "------ Saving the Transaction:\tDONE! "
			
			# Exchanges( self, exchngNo, exchngProduct, exchngQnty,
			#            exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc):
			print "\nSaving the Exchanges -----------"
			for exch in self.sellListStore:
				query = self.session.query(Products).select_from(Products)
				pid = query.filter(Products.name == unicode(exch[1])).first().id
				exchange = Exchanges(utility.getIntegerNumber(exch[0]), pid, utility.getFloatNumber(exch[2]),
									 utility.getFloatNumber(exch[3]), utility.convertToLatin(exch[5]),
									 self.transId, unicode(exch[7]))
				self.session.add( exchange )
				self.session.commit()
				
				#---- Updating the products quantity
				#TODO product quantity shouldbe updated while adding products to factor
				if not self.subPreInv:
					query   = self.session.query(Products).select_from(Products).filter(Products.id == pid)
					pro = query.first()
					pro.quantity -= utility.getFloatNumber(exch[2])
					self.session.commit()
			print "------ Saving the Exchanges:\tDONE! "
			
			if not self.subPreInv:
				print "\nSaving the Document -----------"
				self.registerDocument()

	def checkFullFactor(self):
		if len(self.sellListStore)<1:
			self.statusBar.push(1, "There is no product selected for the invoice.")
			return False
						
		self.subCode    = self.transId
		
		self.subDate    = self.factorDate.getDateObject()
		self.subPreInv  = self.builder.get_object("preChkBx").get_active()
		if not self.subPreInv:
			print "full invoice!"
			pro_dic = {}
			for exch in self.sellListStore:
				pro_name = unicode(exch[1])
				pro_qnty = utility.getFloatNumber(exch[2])
				
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
		
		self.subAdd     = self.additionsEntry.get_float()
		self.subSub     = self.subsEntry.get_float()
		self.subTax     = utility.getFloatNumber(self.taxEntry.get_text())
		self.subShpDate = self.shippedDate.getDateObject()
		self.subFOB     = unicode(self.builder.get_object("FOBEntry").get_text())
		self.subShipVia = unicode(self.builder.get_object("shipViaEntry").get_text())
		self.subDesc    = unicode(self.builder.get_object("transDescEntry").get_text())
		
		self.payableAmnt = utility.getFloatNumber(self.payableAmntEntry.get_text())
		self.totalDisc = utility.getFloatNumber(self.totalDiscsEntry.get_text())
		self.totalPayment = utility.getFloatNumber(self.totalPaymentsEntry.get_text())
		self.statusBar.push(1,"")
		return True

	def registerDocument(self):
		dbconf = dbconfig.dbConfig()
		
		# Find last document number
		query = config.db.session.query(Bill.id, Bill.number).select_from(Bill)
		lastnumber = query.order_by(Bill.number.desc()).first()
		if lastnumber != None:
			bill_id = lastnumber[0] + 1
			doc_number = lastnumber[1] + 1
		else:
			bill_id = 1
			doc_number = 1
		
		# Create new document
		bill = Bill(doc_number, self.subDate, self.subDate, self.subDate, False)
		self.session.add(bill)
		print "bill id is %d" % bill_id
		
		# Assign document to the current transaction
		query = self.session.query(Transactions).select_from(Transactions)
		query = query.filter(Transactions.transId == self.transId)
		query.update( {Transactions.transBill : bill_id } )
		
		query = self.session.query(Cheque).select_from(Cheque)
		query = query.filter(Cheque.chqTransId == self.transId)
		query.update( {Cheque.chqBillId : bill_id } )
		
		query = self.session.query(Payment).select_from(Payment)
		query = query.filter(Payment.paymntTransId == self.transId)
		query.update( {Payment.paymntBillId : bill_id } )
		
		# Create document rows
		doc_rows = []
		trans_code = utility.showNumber(self.subCode, False)
		
		row = Notebook(self.custSubj, bill_id, -(self.payableAmnt), 
		               _("Debit for invoice number %s") % trans_code)
		doc_rows.append(row)
		row = Notebook(dbconf.get_int("sell-discount"), bill_id, -(self.totalDisc + self.subSub), 
		               _("Discount for invoice number %s") % trans_code)
		doc_rows.append(row)
		row = Notebook(dbconf.get_int("sell-adds"), bill_id, self.subAdd, 
		               _("Additions for invoice number %s") % trans_code)
		doc_rows.append(row)
		row = Notebook(dbconf.get_int("tax"), bill_id, self.subTax, 
		               _("Taxes for invoice number %s") % trans_code)
		doc_rows.append(row)
		
		# Create a row for each sold product
		for exch in self.sellListStore:
			query = self.session.query(ProductGroups.sellId)
			query = query.select_from(outerjoin(Products, ProductGroups, Products.accGroup == ProductGroups.id))
			result = query.filter(Products.name == unicode(exch[1])).first()
			sellid = result[0]
			
			exch_totalAmnt = utility.getFloatNumber(exch[2]) * utility.getFloatNumber(exch[3])
			#TODO Use unit name specified for each product
			row = Notebook(sellid, bill_id, exch_totalAmnt, 
			               _("Selling %s units, invoice number %s") 
			               % (exch[2], trans_code) )
			doc_rows.append(row)
			
		# Create rows for payments
		row = Notebook(self.custSubj, bill_id, self.totalPayment, 
		               _("Payment for invoice number %s") % trans_code)
		doc_rows.append(row)
		row = Notebook(dbconf.get_int("fund"), bill_id, -(self.cashPayment), 
		               _("Cash Payment for invoice number %s") % trans_code)
		doc_rows.append(row)
		row = Notebook(dbconf.get_int("acc-receivable"), bill_id, 
		               -(self.totalPayment - self.cashPayment), 
		               _("Non-cash Payment for invoice number %s") % trans_code)
		doc_rows.append(row)
		
		#TODO Add rows for customer introducer's commision
		
		self.session.add_all(doc_rows)
		self.session.commit()

	def printTransaction(self,sender=0):
		print "main page \"PRINT button\" is pressed!", sender

	def paymentsChanged(self, sender=0, ev=0):
		ttlCash = self.cashPymntsEntry.get_float()
		self.cashPayment = ttlCash
		ttlNonCash  = utility.getFloatNumber(self.nonCashPymntsEntry.get_text())
		ttlPayments = ttlCash + ttlNonCash
		
		self.totalPaymentsEntry.set_text(utility.showNumber(ttlPayments))
		self.calculateBalance()
		

	def showPayments(self,sender):
		self.paymentManager.showPayments()
		self.ttlNonCashEntry = self.builder.get_object("ttlNonCashEntry")

	def setNonCashPayments(self, sender, str_value):
		self.nonCashPymntsEntry.set_text(str_value)

