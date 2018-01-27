#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import setuptools

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
if not os.path.exists("locale/"):
    os.mkdir("locale/")
for lang in ('fa', 'fr', 'he', 'tr'):
    pofile = "po/" + lang + ".po"
    locale = "locale/" + lang + "/amir.mo"
    if not os.path.exists("locale/" + lang + "/"):
        os.mkdir("locale/" + lang + "/")
    print "generating", locale
    os.system("msgfmt %s -o %s" % (pofile, locale))

setuptools.setup(
        name = 'amir',
        version = '0.2.0',
        description = 'Amir accounting software',
        author = 'Jooyeshgar',
        author_email = 'info@jooyeshgar.com',
        maintainer = 'Jooyeshgar',
        url = 'https://github.com/jooyeshgar/amir',
        install_requires=['sqlalchemy-migrate>=0.9.0', 'sqlalchemy>=1.0.0'],
        classifiers = [
            'Intended Audience :: End Users/Desktop',
            'License :: GNU General Public License v3.0 (GPL-3)',
            'Programming Language :: Python',
            ],
        packages = setuptools.find_packages(),
        package_data = {'amir': ['data/ui/*.glade', 'data/ui/*.glade.h', 'data/media/*.png', 'data/media/icon/*.png', 'data/amir_migrate/*.py', 'data/amir_migrate/*.cfg', 'data/amir_migrate/versions/*.py']},
        keywords = 'amir accounting',
        scripts = ['scripts/amir'],
        data_files = [
            ('/usr/share/locale/fa/LC_MESSAGES', ['locale/fa/amir.mo']),
            ('/usr/share/locale/fr/LC_MESSAGES', ['locale/fr/amir.mo']),
            ('/usr/share/locale/he/LC_MESSAGES', ['locale/he/amir.mo']),
            ('/usr/share/locale/tr/LC_MESSAGES', ['locale/tr/amir.mo'])]
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
