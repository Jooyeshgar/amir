import sys
import os

import  warehousing
import  numberentry
from    dateentry       import  *
import  subjects
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
        self.builder    = get_builder(      "SellingForm"               )
        self.session    = config.db.session
        
        self.sellsItersDict   = {}
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
        self.transCode.set_text(str(self.transId))
        
        self.factorDate = DateEntry()
        box = self.builder.get_object("datebox")
        box.add(self.factorDate)
        self.factorDate.show()
        
        self.shippedDate = DateEntry()
        shipBox = self.builder.get_object("shippedDateBox")
        shipBox.add(self.shippedDate)
        self.shippedDate.show()
        
        if not transId:
            pass

        self.sellerEntry    = self.builder.get_object("sellerCodeEntry")
        self.totalEntry = self.builder.get_object("subtotalEntry")
        self.totalDiscsEntry    = self.builder.get_object("totalDiscsEntry")
        self.cashPymntsEntry    = self.builder.get_object("cashPymntsEntry")
        self.payableAmntEntry   = self.builder.get_object("payableAmntEntry")
        self.totalPaymentsEntry = self.builder.get_object("totalPaymentsEntry")
        self.remainedAmountEntry= self.builder.get_object("remainedAmountEntry")
        self.nonCashPymntsEntry = self.builder.get_object("nonCashPymntsEntry")
        self.buyerNameEntry     = self.builder.get_object("buyerNameEntry")

        self.addEntry    = self.builder.get_object("additionsEntry")
        self.subsEntry   = self.builder.get_object("subsEntry")
        self.taxEntry    = self.builder.get_object("taxEntry")

        self.statusBar  = self.builder.get_object("sellFormStatusBar")
        
        self.sellsTreeView = self.builder.get_object("sellsTreeView")
        self.sellListStore = gtk.TreeStore(str,str,str,str,str,str,str,str)
        self.sellListStore.clear()
        self.sellsTreeView.set_model(self.sellListStore)
        
        headers = ("No.","Product Name","Quantity","Unit Price","Total Price","Unit Disc.","Disc.","Description")
        txt = 0
        for header in headers:
            column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
            column.set_spacing(5)
            column.set_resizable(True)
            self.sellsTreeView.append_column(column)
            txt += 1
        self.sellsTreeView.get_selection().set_mode(  gtk.SELECTION_SINGLE    )
        
        self.paysTreeView = self.builder.get_object("paymentsTreeView")
        self.paysListStore = gtk.TreeStore(str,str,str,str,str,str,str,str,str)
        self.paysListStore.clear()
        self.paysTreeView.set_model(self.paysListStore)
        
        payHeaders = ("No.","Paid by","Amount","Writing date","Due Date","Bank","Serial No.","Track Code","Description")
        txt = 0
        for header in payHeaders:
            column = gtk.TreeViewColumn(header,gtk.CellRendererText(),text = txt)
            column.set_spacing(5)
            column.set_resizable(True)
            self.paysTreeView.append_column(column)
            txt += 1
        
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
        oldPrice    = float(self.totalEntry.get_text())
        totalPrce   = oldPrice + price
        self.totalEntry.set_text(str(totalPrce))

    def appendDiscount(self, discount):
        oldDiscount = float(self.totalDiscsEntry.get_text())
        oldDiscount = oldDiscount + float(discount) 
        self.totalDiscsEntry.set_text(str(oldDiscount))
        
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
                while No < length:#len(self.sellsItersDict):
                    print No
#                    if self.sellsItersDict.has_key(No+1):
                    nextIter    = self.sellsItersDict[No+1]
                    self.sellListStore.set_value(nextIter,0,str(No))
                    self.sellsItersDict[No] = nextIter
                    del self.sellsItersDict[No+1]
                    No  += 1
                print "--------------",length
            else:
                self.sellsItersDict = {}
                
    def reducePrice(self,  price):
        oldPrice    = float(self.totalEntry.get_text())
        totalPrce   = oldPrice - price
        self.totalEntry.set_text(str(totalPrce))

    def reduceDiscount(self, discount):
        oldDiscount = float(self.totalDiscsEntry.get_text())
        oldDiscount = oldDiscount - discount
        self.totalDiscsEntry.set_text(str(oldDiscount))

    def addSell(self,sender=0,edit=None):
        self.addSellDlg = self.builder.get_object("addASellDlg")
        if edit:
            self.editCde    = edit[0]
            ttl = "Edit sell:\t%s - %s" %(self.editCde,edit[1])
            self.addSellDlg.set_title(ttl)
            self.edtSellFlg = True
            self.oldTtl     = edit[4] 
            self.oldTtlDisc = edit[6]
            btnVal  = "Save Changes..."
        else:
            self.editingSell    = None
            self.addSellDlg.set_title("Choose sell information")
            self.edtSellFlg = False
            btnVal  = "Add to list"
        self.proVal     = self.builder.get_object("proEntry")
        self.qntyVal    = self.builder.get_object("qntyVal")
        self.untPrcVal  = self.builder.get_object("unitPriceVal")
        self.discVal    = self.builder.get_object("discVal")
        self.descVal    = self.builder.get_object("descVal")
        self.avQntyVal  = self.builder.get_object("availableQntyVal")
        self.stnrdDisc  = self.builder.get_object("stnrdDiscVal")
        self.stndrdPVal = self.builder.get_object("stnrdSelPrceVal")
        self.discTtlVal = self.builder.get_object("discTtlVal")
        self.ttlAmntVal = self.builder.get_object("totalAmontVal")
        self.ttlPyblVal = self.builder.get_object("totalPyableVal")
        self.btn        = self.builder.get_object("okBtn")
        self.btn.set_label(btnVal)
        self.addSellDlg.show_all()
        
        self.proNameLbl = self.builder.get_object("proNameLbl")
        self.proNameLbl.hide()
        self.addSellStBar   = self.builder.get_object("addSellStatusBar")
        self.addSellStBar.push(1,"")
        self.availableQntyBox   = self.builder.get_object("availableQntyBox")
        self.availableQntyBox.hide()
        self.stnrdSelPrceBox    = self.builder.get_object("stnrdSelPrceBox")
        self.stnrdSelPrceBox.hide()
        self.discTtlBox = self.builder.get_object("discTtlBox")
        
        self.stnrdDiscBox = self.builder.get_object("stnrdDiscBox")
        self.stnrdDiscBox.hide()
        
        self.proVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.qntyVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.discVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        
        if self.edtSellFlg:
            (No,pName,qnty,untPrc,ttlPrc,untDisc,ttlDisc,desc) = edit
            pName   = unicode(pName)
            pro = self.session.query(Products).select_from(Products).filter(Products.name==pName).first()
            self.proSelected(code=pro.code)
            self.proVal.set_text(pro.code)
            self.qntyVal.set_text(qnty)
            self.untPrcVal.set_text(untPrc)
            self.discVal.set_text(untDisc)
            self.descVal.set_text(desc)
            self.untPrcVal.set_text(untPrc)
            self.validateBuy()
                
    def cancelSell(self,sender=0,ev=0):
        self.proVal.set_text("")
        self.qntyVal.set_text("0.0")
        self.untPrcVal.set_text("0.0")
        self.discVal.set_text("0.0")
        self.ttlAmntVal.set_text("0.0")
        self.discTtlVal.set_text("0.0")
        self.ttlPyblVal.set_text("0.0")
        self.descVal.set_text("")
        self.addSellDlg.hide_all()
        return True

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
        qnty    = float(self.qntyVal.get_text())
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
                return
        slPrc   = float(self.untPrcVal.get_text())
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
        total   = qnty*slPrc
        descp   = self.descVal.get_text()
        untDisc = self.discVal.get_text()
        if self.edtSellFlg:
            No  = self.editCde
            sellList    = (str(No),productName,str(qnty),str(slPrc),str(total),untDisc,discnt,descp)
            for i in range(len(sellList)):
                self.sellListStore.set(self.editingSell,i,sellList[i])
#            editedIter  = self.sellListStore.set(None,sellList)
            self.reducePrice(float(self.oldTtl))
            self.reduceDiscount(float(self.oldTtlDisc))
            self.appendPrice(total)
            self.appendDiscount(discnt)
            self.valsChanged()
#            self.sellsDict[No]  = (self.editingSell,product,sellList)
            self.sellsItersDict[No]   = self.editingSell
            self.cancelSell()
            
        else:
            No  = len(self.sellsItersDict) + 1
            sellList    = (str(No),productName,str(qnty),str(slPrc),str(total),untDisc,discnt,descp)
            iter    = self.sellListStore.append(None,sellList)
            self.appendPrice(total)
            self.appendDiscount(discnt)
            self.valsChanged()
#            self.sellsDict[No]  = (iter,product,sellList)
            self.sellsItersDict[No]   = iter
            self.cancelSell()

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
        subtotal    = float(self.builder.get_object("subtotalEntry").get_text())
        ttlDiscs    = float(self.builder.get_object("totalDiscsEntry").get_text())
        addEntry    = self.addEntry
        subsEntry   = self.subsEntry
        taxEntry    = self.taxEntry
        err         = False
        try:
            additions   = float(addEntry.get_text())
            addEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            addEntry.set_tooltip_text("")
        except:
            addEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
            addEntry.set_tooltip_text("Invalid Number")
            err     = True

        try:
            substracts   = float(subsEntry.get_text())
            subsEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            subsEntry.set_tooltip_text("")
        except:
            subsEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
            subsEntry.set_tooltip_text("Invalid Number")
            err     = True
        
        try:
            tax   = float(taxEntry.get_text())
            taxEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            taxEntry.set_tooltip_text("")
        except:
            taxEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
            taxEntry.set_tooltip_text("Invalid Number")
            err     = True

        if not err:
            amnt    = subtotal + additions + tax - substracts - ttlDiscs
            self.payableAmntEntry.set_text(str(amnt))

    def calculateBalance(self):
        payableAmnt = float(self.payableAmntEntry.get_text())
        ttlPayment  = float(self.totalPaymentsEntry.get_text())
        blnc        = payableAmnt - ttlPayment
        blncDue     = self.remainedAmountEntry.set_text(str(blnc))
                
    def keyPressedEvent(self,sender=0,ev=0):
        if ev.keyval == 65293 or ev.keyval == 65421:
            self.validateBuy()
            
    def valsChanged(self,sender=0,ev=0):
        self.calculatePayable()
        self.calculateBalance()

    def validateBuy(self,sender=0,ev=0):
        #------------- Validate Product:
        stMsg   = ""
        productCd   = self.proVal.get_text()
        product = self.session.query(Products).select_from(Products).filter(Products.code==productCd).first()
        if not product:
            self.proVal.modify_base(gtk.STATE_NORMAL,self.redClr)
            self.proVal.set_tooltip_text("Product code is invalid")
            self.addSellStBar.push(1,"Product code is invalid")
            self.proNameLbl.set_text("")
            return
        else:
            self.proVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            self.proVal.set_tooltip_text("")
            self.proSelected(code=product.code)
            self.proNameLbl.set_text(str(product.name))
        
        #------------- Validate Quantity:
        qnty    = None
        try:
            if self.qntyVal.get_text() == "":
                self.qntyVal.set_text("0.0")
            qnty    = float(self.qntyVal.get_text())
            self.qntyVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            self.qntyVal.set_tooltip_text("")

        except:
            self.qntyVal.modify_base(gtk.STATE_NORMAL,self.redClr)
            self.qntyVal.set_tooltip_text("Quantity is not valid")
            if not stMsg:
                stMsg   = "Quantity is not valid"

        if qnty != None:
            qntyAvlble  = float(product.quantity)
            over    = product.oversell
            if qnty < 0:
                self.qntyVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                if not stMsg:
                    stMsg  = "Quantity must be greater than 0."
                self.qntyVal.set_tooltip_text("Quantity must be greater than 0.")

            elif qnty > qntyAvlble and not over:
                self.qntyVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                msg = "Quantity is more than the available storage. (Over-Sell is Off)"
                if not stMsg:
                    stMsg  = msg
                self.qntyVal.set_tooltip_text(msg)

            else:
                self.qntyVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
                self.qntyVal.set_tooltip_text("")
                self.addSellStBar.push(1,"")
        
        #------------- Validate Unit Price:
        untPrc  = None
        try:
            untPrc  = float(self.untPrcVal.get_text())
            self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            self.untPrcVal.set_tooltip_text("")
            self.addSellStBar.push(1,"")            
        except:
            self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.redClr)
            self.untPrcVal.set_tooltip_text("Unit Price not valid")
            if not stMsg:
                stMsg  = "Unit Price not valid"

        if untPrc != None:
            purcPrc = product.purchacePrice
            if untPrc < 0:
                self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                erMsg  = "Unit Price cannot be negative."
                self.untPrcVal.set_tooltip_text(erMsg)
                if not stMsg:
                    stMsg   = erMsg

            elif untPrc < purcPrc:
                self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                err  = "Unit Price is less than the product purchase price."
                self.untPrcVal.set_tooltip_text(err)
                if not stMsg:
                    stMsg  = err

            else:
                self.untPrcVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
                self.untPrcVal.set_tooltip_text("")
        
        #------------- Validate discount:
        disc    = None
        try:
            disc  = float(self.discVal.get_text())
            self.discVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            self.discVal.set_tooltip_text("")
        except:
            self.discVal.modify_base(gtk.STATE_NORMAL,self.redClr)
            self.discVal.set_tooltip_text("Invalid Value")

        if disc != None:
            if disc > 100 or disc < 0:
                self.discVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                errMess  = "Invalid discount range. (Discount must be between 0 and 100 percent)"
                self.discVal.set_tooltip_text(errMess)
                if not stMsg:
                    stMsg  = errMess

            elif (untPrc * ((100 - disc) /100)) < purcPrc:
                self.discVal.modify_base(gtk.STATE_NORMAL,self.redClr)
                errMess  = "The ( unit price * Discount ) would be result less than the product purchase price!"
                self.discVal.set_tooltip_text(errMess)
                if not stMsg:
                    stMsg  = errMess
            else:
                self.discVal.modify_base(gtk.STATE_NORMAL,self.whiteClr)
                self.discVal.set_tooltip_text("")
        
        self.addSellStBar.push(1,stMsg)
        if not stMsg:
            self.calcTotal()
            self.calcTotalDiscount()
        
    def proDeselected(self):
        self.proNameLbl.hide()
        self.stnrdSelPrceBox.hide()
        self.availableQntyBox.hide()
        self.stnrdDiscBox.hide()
    
    def proSelected(self,sender=0, id=0, code=0):
        selectedPro = self.session.query(Products).select_from(Products).filter(Products.code==code).first()
        id      = selectedPro.id
        code    = selectedPro.code
        name    = selectedPro.name
        qnty    = float(selectedPro.quantity)
        sellPrc = float(selectedPro.sellingPrice)
        discnt  = selectedPro.discountFormula
        if not discnt:
            discnt  = "0"
        disc    = float(discnt)
        
        self.avQntyVal.set_text(str(qnty))
        self.stnrdDisc.set_text(str(disc))
        if self.untPrcVal.get_text() == "0.0":
            self.untPrcVal.set_text(str(sellPrc))
        if self.discVal.get_text() == "0.0":
            self.discVal.set_text(str(disc))

        self.stndrdPVal.set_text(str(sellPrc))

        self.proNameLbl.show()
        self.stnrdSelPrceBox.show()
        self.availableQntyBox.show()
        self.stnrdDiscBox.show()
        
        if sender:
            self.proVal.set_text(code)
            sender.viewProsWin.destroy()
    
    def calcTotal(self):
        unitPrice   = float(self.untPrcVal.get_text())
        qnty        = float(self.qntyVal.get_text())
        total       = unitPrice * qnty
        self.ttlAmntVal.set_text(str(total))
        self.calcTotalPayable()

    def calcTotalDiscount(self):
        discPerCnt  = float(self.discVal.get_text())
        unitPrice   = float(self.untPrcVal.get_text())
        qnty        = float(self.qntyVal.get_text())
        totalDisc   = float((discPerCnt * unitPrice * qnty)/100)
        self.discTtlVal.set_text(str(totalDisc))
        self.calcTotalPayable()
    
    def calcTotalPayable(self):
        ttlAmnt     = float(self.ttlAmntVal.get_text())
        discVal     = float(self.discTtlVal.get_text())
        self.ttlPyblVal.set_text(str(ttlAmnt - discVal))

    def selectProduct(self,sender=0):
        obj = warehousing.Warehousing()
        obj.viewProducts()
        obj.connect("product-selected",self.proSelected)
    
    def close(self, sender=0):
        self.mainDlg.destroy()

    def selectSeller(self,sender=0):
        subject_win = subjects.Subjects()
        code = self.sellerEntry.get_text()
        if code != '':
            subject_win.highlightSubject(code)
        subject_win.connect("subject-selected",self.sellerSelected)
        
    def sellerSelected(self, sender, id, code, name):
        self.sellerEntry.set_text(code)
        sender.window.destroy()
        self.buyerNameEntry.set_text(name)

    def setSellerName(self,sender=0,ev=0):
        payer   = self.sellerEntry.get_text()
        query   = self.session.query(Subject).select_from(Subject)
        query   = query.filter(Subject.code==payer).first()
        if not query:
            self.buyerNameEntry.set_text("")
        else:
            self.buyerNameEntry.set_text(query.name)

    def submitFactorPressed(self,sender):
        permit  = self.checkFullFactor()
        if permit:
            print "--------- Starting... ------------"
            print "\nSaving the Transaction ----------"
            sell = Transactions( self.subCode, self.subDate, self.subCustId, self.subAdd,
                                 self.subSub, self.subTax, self.subShpDate, self.subFOB,
                                 self.subShipVia, self.subPreInv, self.subDesc )
            self.session.add( sell )
            self.session.commit()
            print "------ Saving the Transaction:\tDONE! "
#                Exchanges( self, exchngNo, exchngProduct, exchngQnty,
#                  exchngUntPrc, exchngUntDisc, exchngTransId, exchngDesc):
            print "\nSaving the Exchanges -----------"
            for exch in self.sellListStore:
                id = self.session.query(Products).select_from(Products).filter(Products.name==unicode(exch[1])).first().id
                exchange = Exchanges( int(exch[0]), id, float(exch[2]), float(exch[3]),
                                      float(exch[5]), self.transId, unicode(exch[7]))
                self.session.add( exchange )
                self.session.commit()
                #---- Updating the products quantity
                if not self.subPreInv:
                    query   = self.session.query(Products).select_from(Products).filter(Products.id==id)
                    oldQnty = query.first().quantity
                    newQnty = oldQnty - float(exch[2])
                    updateVals  = { Products.quantity : newQnty }
                    edit    = query.update( updateVals )
                    self.session.commit()
            print "------ Saving the Exchanges:\tDONE! "
#                pay = Payments( paymntNo, paymntDueDate, paymntBank, paymntSerial, paymntAmount,
#                  paymntPayer, paymntWrtDate, paymntDesc, paymntTransId, paymntTrckCode ):
            print "\nSaving the Payments -----------"
            for payment in self.paysListStore:
                dueDt = stringToDate(payment[4])
                #------ Must Change to check this from the customers
                subId = self.session.query(Subject).select_from(Subject).filter(Subject.name==unicode(payment[1])).first().id
                #-----------------
                wrtDt = stringToDate(payment[3])
                pay = Payments( int(payment[0]), dueDt, unicode(payment[5]), unicode(payment[6]), float(payment[2]),
                                subId, wrtDt, unicode(payment[8]), self.transId, unicode(payment[7]) )
                self.session.add( pay )
                self.session.commit()
            print "------ Saving the Payments:\tDONE! "


    def checkFullFactor(self):
        if len(self.sellListStore)<1:
            self.statusBar.push(1, "There is no product selected for the invoice.")
            return False
                        
        self.subCode    = self.transCode.get_text()
        
        self.subDate    = self.factorDate.getDateObject()
        self.subPreInv  = self.builder.get_object("preChkBx").get_active()
        self.subCust    = self.sellerEntry.get_text()
        query   = self.session.query(Subject).select_from(Subject).filter(Subject.code==self.subCust).first()
        if not query:
            self.statusBar.push(1, "Customer Code is not valid")
            return False
        else:
            self.subCustId  = query.id #query.custId
        
        self.subAdd     = self.addEntry.get_text()
        self.subSub     = self.subsEntry.get_text()
        self.subTax     = self.taxEntry.get_text()
        self.subShpDate = self.shippedDate.getDateObject()
        self.subFOB     = unicode(self.builder.get_object("FOBEntry").get_text())
        self.subShipVia = unicode(self.builder.get_object("shipViaEntry").get_text())
        self.subDesc    = unicode(self.builder.get_object("transDescEntry").get_text())
        return True
    
    def printTransaction(self,sender=0):
        print "main page \"PRINT button\" is pressed!", sender
             
    def addPayment(self,sender=0,edit=None):
        self.addPymntDlg = self.builder.get_object("addPaymentDlg")
        if edit:
            self.editPymntNo    = edit[0]
            ttl = "Edit Non-Cash Payment:\t%s - %s" %(self.editPymntNo,edit[1])
            self.addPymntDlg.set_title(ttl)
            self.edtPymntFlg = True
            btnVal  = "Save Changes..."
        else:
            self.editingPay = None
            self.addPymntDlg.set_title("Add Non-Cash Payment")
            self.edtPymntFlg = False
            btnVal  = "Add payment to list"
        self.payerEntry     = self.builder.get_object("payerEntry")
        self.pymntAmntEntry = self.builder.get_object("pymntAmntEntry")
        
        self.pymntDueDateBox  = self.builder.get_object("pymntDueDateBox")
        self.pymntDueDateEntry  = DateEntry()#dateentry.DateEntry()
        self.pymntDueDateBox.add(self.pymntDueDateEntry)
        self.pymntDueDateEntry.show()
        today   = date.today()
        self.pymntDueDateEntry.showDateObject(today)
        
        self.pymntWritingDateBox   = self.builder.get_object("pymntWritingDateBox")
        self.writingDateEntry  = DateEntry()#dateentry.DateEntry()
        self.pymntWritingDateBox.add(self.writingDateEntry)
        self.writingDateEntry.show()
        
        self.pymntDescEntry = self.builder.get_object("pymntDescEntry")
        self.bankEntry  = self.builder.get_object("bankEntry")
        self.serialNoEntry  = self.builder.get_object("serialNoEntry")
        self.chqPayerLbl    = self.builder.get_object("chqPayerLbl")
        self.trackingCodeEntry  = self.builder.get_object("trackingCodeEntry")
        
        self.payerEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.writingDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntDueDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.bankEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.serialNoEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntDescEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        
        self.btn    = self.builder.get_object("submitBtn")
        self.btn.set_label(btnVal)
        
        self.pymntStBar   = self.builder.get_object("paymentsStatusBar")
        self.pymntStBar.push(1,"")
        self.addPymntDlg.show_all()
        
        self.payerEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntAmntEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntDueDateEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
        self.pymntDescEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)

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
    
    def addNonCashTtl(self,amnt):
        lstAmnt = float(self.ttlNonCashEntry.get_text())
        amount  = lstAmnt + amnt
        self.ttlNonCashEntry.set_text(str(amount))
        self.nonCashPymntsEntry.set_text(str(amount))
        self.paymentsChanged()
        
    def remNonCashTtl(self,amnt):
        lstAmnt = float(self.ttlNonCashEntry.get_text())
        amount  = lstAmnt - amnt
        self.ttlNonCashEntry.set_text(str(amount))
        self.nonCashPymntsEntry.set_text(str(amount))
        self.paymentsChanged()
        
    def paymentsChanged(self,sender=0,ev=0):
        try:
            ttlCash = float(self.cashPymntsEntry.get_text())
            self.cashPymntsEntry.modify_base(gtk.STATE_NORMAL,self.whiteClr)
            self.statusBar.push(1,"")
            self.cashPymntsEntry.set_tooltip_text("")
        except:
            self.cashPymntsEntry.modify_base(gtk.STATE_NORMAL,self.redClr)
            msg = "Invalid Value for the cash payments..."
            self.statusBar.push(1,msg)
            self.cashPymntsEntry.set_tooltip_text(msg)
            return        
        ttlNonCash  = float(self.nonCashPymntsEntry.get_text())
        ttlPayments = ttlCash + ttlNonCash
        self.totalPaymentsEntry.set_text(str(ttlPayments))
        self.calculateBalance()
    
    def showPayments(self,sender):
        self.showPymnts = self.builder.get_object("showPymnts")
        self.ttlNonCashEntry = self.builder.get_object("ttlNonCashEntry")
        self.showPymnts.show_all()
    
    def hidePayments(self,sender=0,ev=0):
        self.showPymnts.hide_all()
        return True

    def cancelPayment(self,sender=0,ev=0):
        self.payerEntry.set_text("")
        self.pymntAmntEntry.set_text("0.0")
        self.writingDateEntry.set_text("")
        self.pymntDueDateEntry.set_text("")
        self.bankEntry.set_text("")
        self.serialNoEntry.set_text("")
        self.pymntDescEntry.set_text("")
        self.trackingCodeEntry.set_text("")
        self.chqPayerLbl.set_text("")
        
        self.pymntDueDateEntry.destroy()
        self.writingDateEntry.destroy()

        self.addPymntDlg.hide_all()
        return True

    def selectPayer(self,sender=0):
        subject_win = subjects.Subjects()
        code = self.payerEntry.get_text()
        if code != '':
            subject_win.highlightSubject(code)
        subject_win.connect("subject-selected",self.payerSelected)
        
    def payerSelected(self, sender, id, code, name):
        self.payerEntry.set_text(code)
        self.chqPayerLbl.set_text(name)
        sender.window.destroy()        
