#!/bin/sh
xgettext -k_ -kN_ -o po/amir.pot amir/*.py amir/database/*.py bin/amir data/ui/*.glade

#msgfmt po/*.po 
