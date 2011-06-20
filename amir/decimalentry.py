#-*- encoding: utf-8 -*-

import pygtk
import gtk
import gobject

import utility

from string import replace

class DecimalEntry(gtk.Entry):
    """
        Creates a text entry widget that just accepts number keys. no dots, spaces or commas.
        Please consider this class usage in other classes before changing this behaviour.
    """
    
    def __init__(self, Max=0):
        gtk.Entry.__init__(self, Max)
        self.insert_sig = self.connect("insert-text", self.insert_cb)
    
    def insert(self, widget, text, pos):
    # the next three lines set up the text. this is done because we
    # can't use insert_text(): it always inserts at position zero.
        orig_text = unicode(widget.get_text())
        text = unicode(text)
        new_text = orig_text[:pos] + text + orig_text[pos:]
        try:
            float(new_text.replace('/', '.'))
        except ValueError:
            new_text = orig_text
            
        
    # avoid recursive calls triggered by set_text
        widget.handler_block(self.insert_sig)
    # replace the text with some new text
        widget.set_text(new_text)
        widget.handler_unblock(self.insert_sig)
    # set the correct position in the widget
        widget.set_position(pos + len(text))
       
    def insert_cb(self, widget, text, length, position):
    # if you don't do this, garbage comes in with text
        text = text[:length]
        pos = widget.get_position()
    # stop default emission
        widget.emit_stop_by_name("insert_text")
        gobject.idle_add(self.insert, widget, text, pos)

    def get_int(self):
        #--- This method will return the integer format of the entered  
        #--- value. If there is no text entered, 0 will be returned.
        try:
            val = int(unicode(self.get_text()).replace('/', '.'))
        except:
            val = 0
        return val

    def get_float(self):
        try:
            return float(unicode(self.get_text()).replace('/', '.'))
        except:
            return 0
        
    def is_numeric(self):
        try:
            float(readNumber())
            return True
        except ValueError:
            return False

    #def readNumber (self):
        #str = self.get_text()
        #en_numbers = '0123456789'
        #fa_numbers = u'۰۱۲۳۴۵۶۷۸۹'
        
        #for c in fa_numbers:
            #str = replace(str,c,en_numbers[fa_numbers.index(c)])
            
        #return str
 