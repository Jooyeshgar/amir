#!/bin/sh
echo "ss;sdj"
xgettext -k_ -kN_ -o po/amir.pot amir/*.py amir/database/*.py scripts/amir amir/data/ui/*.glade

#msgfmt po/*.po 
