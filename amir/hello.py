#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2010 <jooyeshgar> <info@jooyeshgar.com>
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import pygtk
pygtk.require('2.0')
import gtk
import database
import gettext,locale

# Check if we are working in the source tree or from the installed 
# package and mangle the python path accordingly
if os.path.dirname(sys.argv[0]) != ".":
    if sys.argv[0][0] == "/":
        fullPath = os.path.dirname(sys.argv[0])
    else:
        fullPath = os.getcwd() + "/" + os.path.dirname(sys.argv[0])
else:
    fullPath = os.getcwd()
sys.path.insert(0, os.path.dirname(fullPath))

from amir import Subjects, AddEditDoc
from amir.amirconfig import getdatapath

class AmirWindow(gtk.Window):
    __gtype_name__ = "AmirWindow"

    def __init__(self):
    	pass
    	
    def manualDocument(self, sender):
        dialog = addeditdoc.AddEditDoc()

    def quitMainWindow(self, sender):
        pass
    def aboutAmir(self, sender):
        pass
    def manageSubjects(self, sender):
        dialog = subjects.Subjects()
        print ("notebook subjects clicked")
        
    def settingsDialog(self, sender):
        pass
    
    def view_toolbar(self, sender):
        dialog = subjects.Subjects()
        print ("view toolbar clicked")
        db = database.db
        users = db.session.query(database.User).all()
        for user in users:
            print user.age
        
    def hello(self, widget, data=None):
        print ("Hello World")

    def delete_event(self, widget, event, data=None):
        
     ##TODO uncomment later  
        #=======================================================================
        # msgbox = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, "Are you sure to close the app?")
        # msgbox.set_title("Are you sure?")
        # result = msgbox.run();
        # if result == gtk.RESPONSE_CANCEL :
        #    msgbox.destroy()
        #    return True
        # else :
        #    return False
        #=======================================================================

        return False
        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".

    def destroy(self, widget, data=None):
        print ("destroy signal occurred")
        gtk.main_quit()

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("amir")
        self.builder.add_from_file("../data/mainwin.glade")
        self.window = self.builder.get_object("window1")
        initial = self.builder.get_object("menubar2")
        initial.hide()
        self.builder.connect_signals(self)
        
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    gettext.install('amir', '/usr/share/locale')
    parser = optparse.OptionParser(version="%prog %ver")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Show debug messages")
    (options, args) = parser.parse_args()
    
    #set the logging level to show debug messages
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('logging enabled')

     mainwin = MainWindow()
     mainwin.main()

