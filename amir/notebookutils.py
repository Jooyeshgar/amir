import gi
from gi.repository import Gtk
import datetime

from sqlalchemy import or_, and_
from sqlalchemy.orm.util import outerjoin

from database import *
from share import share

config = share.config

def arrangeDocuments(parentWin):
    msg = _("This operation may change numbers of permanent documents too.\n\nAre you sure to continue?")
    msgbox = Gtk.MessageDialog(parentWin, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, msg)
    msgbox.set_title(_("Changing document numbers"))
    result = msgbox.run()
    msgbox.destroy()
    if result == Gtk.ResponseType.CANCEL:
        return
    
    query = config.db.session.query(Bill).select_from(Bill)
    query = query.order_by(Bill.date.asc(), Bill.number.asc())
    result = query.all()
    
    num_index = 1
    for b in result:
        b.number = num_index
        num_index += 1
        config.db.session.add(b)
        
    config.db.session.commit()   
    msg = _("Ordering documents completed successfully.")
    msgbox = Gtk.MessageDialog(parentWin, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
    msgbox.set_title(_("Operation successfull"))
    result = msgbox.run()
    msgbox.destroy()      
    
