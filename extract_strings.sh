#!/bin/sh
xgettext -k_ -kN_ -o po/messages.pot amir/*.py bin/amir data/ui/*.glade

/usr/lib/pymodules/python2.6/formencode/i18n/msgfmt.py po/*.po 
