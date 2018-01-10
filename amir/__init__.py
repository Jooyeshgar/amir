import os, logging
import pygtk
pygtk.require('2.0')
import gtk,gtk.glade
import gettext,locale
import gobject
import glib
from amir.amirconfig import AmirConfig
from amir.share import share

config = AmirConfig()
share.config = config
gettext.install('amir', config.locale_path, unicode=1)