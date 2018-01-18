#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup, Extension

def removeall(path):
    if not os.path.isdir(path):
        return

    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            removeall(fullpath)
            f=os.rmdir
            rmgeneric(fullpath, f)

def rmgeneric(path, __func__):
    try:
        __func__(path)
    except OSError, (errno, strerror):
        pass

# Create mo files:
if not os.path.exists("mo/"):
    os.mkdir("mo/")
for lang in ('fa', 'fr', 'he', 'tr'):
    pofile = "po/" + lang + ".po"
    mofile = "mo/" + lang + "/amir.mo"
    if not os.path.exists("mo/" + lang + "/"):
        os.mkdir("mo/" + lang + "/")
    print "generating", mofile
    os.system("msgfmt %s -o %s" % (pofile, mofile))


setup(
        name='amir',
        version='18.01',
        description='Amir accounting software',
        author='Jooyeshgar',
        author_email='info@jooyeshgar.com',
        maintainer= 'Jooyeshgar',
        url='https://launchpad.net/amir',
        install_requires=['migrate', 'tempita', 'sqlalchemy'],
        py_modules = ['amir'],
        classifiers=[
            'Intended Audience :: End Users/Desktop',
            'License :: GNU General Public License v3.0 (GPL-3)',
            'Programming Language :: Python',
            ],
        packages = ['amir', 'amir/database'],
        keywords='amir accounting',
        scripts = ['scripts/amir'],
        data_files=[
            ('share/locale/fa/LC_MESSAGES', ['data/locale/fa/LC_MESSAGES/amir.mo']),
            ('share/locale/fr/LC_MESSAGES', ['data/locale/fr/LC_MESSAGES/amir.mo']),
            ('share/locale/he/LC_MESSAGES', ['data/locale/he/LC_MESSAGES/amir.mo']),
            ('share/locale/tr/LC_MESSAGES', ['data/locale/tr/LC_MESSAGES/amir.mo']),
            ('share/amir/media/icon', ['data/media/icon/16.png']),
            ('share/amir/media/icon', ['data/media/icon/22.png']),
            ('share/amir/media/icon', ['data/media/icon/32.png']),
            ('share/amir/media/icon', ['data/media/icon/48.png']),
            ('share/amir/media/icon', ['data/media/icon/64.png']),
            ('share/amir/media/icon', ['data/media/icon/128.png']),
            ('share/amir/ui', ['data/ui/SellingForm.glade']),
            ('share/amir/ui', ['data/ui/PurchasingForm.glade']),
            ('share/amir/ui', ['data/ui/cheque.glade']),
            ('share/amir/ui', ['data/ui/mainwin.glade']),
            ('share/amir/ui', ['data/ui/setting.glade']),
            ('share/amir/ui', ['data/ui/document.glade']),
            ('share/amir/ui', ['data/ui/customers.glade']),
            ('share/amir/ui', ['data/ui/bankaccounts.glade']),
            ('share/amir/ui', ['data/ui/notebook.glade.h']),
            ('share/amir/ui', ['data/ui/automaticaccounting.glade']),
            ('share/amir/ui', ['data/ui/mainwin.glade.h']),
            ('share/amir/ui', ['data/ui/warehousing.glade']),
            ('share/amir/ui', ['data/ui/notebook.glade']),
            ('share/amir/amir_migrate/versions', ['data/amir_migrate/versions/001_Version_1.py']),
            ('share/amir/amir_migrate/versions', ['data/amir_migrate/versions/002_Version_2.py']),
            ('share/amir/amir_migrate/versions', ['data/amir_migrate/versions/__init__.py']),
            ('share/amir/media', ['data/media/logo.png']),
            ('share/amir/media', ['data/media/background.png']),
            ('share/amir/media', ['data/media/icon.png']),
            ('share/amir/amir_migrate', ['data/amir_migrate/__init__.py']),
            ('share/amir/amir_migrate', ['data/amir_migrate/migrate.cfg']),
            ('share/amir/amir_migrate', ['data/amir_migrate/README']),
            ('share/amir/amir_migrate', ['data/amir_migrate/manage.py'])]
        )


# Cleanup (remove /build, /mo, and *.pyc files:
print "Cleaning up..."
try:
    removeall("build/")
    os.rmdir("build/")
except:
    pass
try:
    removeall("mo/")
    os.rmdir("mo/")
except:
    pass
try:
    for f in os.listdir("."):
        if os.path.isfile(f):
            if os.path.splitext(os.path.basename(f))[1] == ".pyc":
                os.remove(f)
except:
    pass
