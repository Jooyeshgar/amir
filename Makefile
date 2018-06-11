
extract:
	xgettext -k_ -kN_ -L Python -o po/amir.pot amir/*.py amir/database/*.py scripts/amir 
	xgettext -k_ -kN_ -L Glade -o po/amir.pot amir/data/ui/*.glade

fa:
	msgmerge  --backup=none -N -U po/fa.po po/amir.pot

fr:
	msgmerge  --backup=none -N -U po/fr.po po/amir.pot

he:
	msgmerge  --backup=none -N -U po/he.po po/amir.pot

tr:
	msgmerge  --backup=none -N -U po/tr.po po/amir.pot
	
compile:
	msgfmt po/fa.po -o locale/fa/LC_MESSAGES/amir.mo
	msgfmt po/fr.po -o locale/fr/LC_MESSAGES/amir.mo
	msgfmt po/he.po -o locale/he/LC_MESSAGES/amir.mo
	msgfmt po/tr.po -o locale/tr/LC_MESSAGES/amir.mo
