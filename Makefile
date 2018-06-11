
extract:
	xgettext -k_ -kN_ -L Python -o po/amir.pot amir/*.py amir/database/*.py scripts/amir 
	xgettext -k_ -kN_ -L Glade -o po/amir.pot amir/data/ui/*.glade

fa:
	msgmerge  --backup=none -N -U po/fa.po po/amir.pot

en:
	msgmerge  --backup=none -N -U po/en.po po/amir.pot

ar:
	msgmerge  --backup=none -N -U po/ar.po po/amir.pot
	
compile:
	msgfmt po/fa.po -o locale/fa/LC_MESSAGES/amir.mo
	# msgfmt po/en.po -o locale/en/LC_MESSAGES/amir.mo
	# msgfmt po/ar.po -o locale/ar/LC_MESSAGES/amir.mo
