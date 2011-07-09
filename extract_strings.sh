#!/bin/sh
xgettext -k_ -kN_ -o po/amir.pot amir/*.py bin/amir data/ui/*.glade

msgfmt po/*.po 
