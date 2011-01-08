# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

"""Helpers for an Ubuntu application."""

__all__ = [
    'make_window',
    ]

import os
import gtk,logging

#from amir.amirconfig import get_data_file
from amirconfig import config

def get_builder(builder_file_name):
    """Return a fully-instantiated gtk.Builder instance from specified ui 
    file
    
    :param builder_file_name: The name of the builder file, without extension.
        Assumed to be in the 'ui' directory under the data path.
    """
    # Look for the ui file that describes the user interface.
    #ui_filename = get_data_file('ui', '%s.ui' % (builder_file_name,))
    ui_filename = os.path.join(config.data_path, 'ui', '%s.glade' % (builder_file_name,))

    if not os.path.exists(ui_filename):
		logging.error("UI file \"%s\" not found." % ui_filename)
        #ui_filename = None

    builder = gtk.Builder()
    builder.set_translation_domain('amir')
    builder.add_from_file(ui_filename)
    return builder

def comboInsertItems(combo, items):
    ls = gtk.ListStore(str)
    for i in items:
        ls.append([str(i)])
    combo.set_model(ls)
    cellr = gtk.CellRendererText()
    combo.clear()
    combo.pack_start(cellr)
    combo.add_attribute(cellr, 'text', 0)
    
    
