#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
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
    locale_path = "locale/" + lang + "/LC_MESSAGES/amir.mo"
    if not os.path.exists("locale/" + lang + "/LC_MESSAGES/"):
        os.makedirs("locale/" + lang + "/LC_MESSAGES/")
    print "generating", locale_path
    os.system("msgfmt %s -o %s" % (pofile, locale_path))

if platform.system() != 'Windows':
    data = [
        ('/usr/share/locale/fa/LC_MESSAGES', ['locale/fa/LC_MESSAGES/amir.mo']),
        ('/usr/share/locale/fr/LC_MESSAGES', ['locale/fr/LC_MESSAGES/amir.mo']),
        ('/usr/share/locale/he/LC_MESSAGES', ['locale/he/LC_MESSAGES/amir.mo']),
        ('/usr/share/locale/tr/LC_MESSAGES', ['locale/tr/LC_MESSAGES/amir.mo'])]
else:
    data = []

setuptools.setup(
        name = 'amir',
        version = '0.3.0',
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
        package_data = {'amir': ['data/ui/*.glade', 'data/ui/*.glade.h', 'data/media/*.png', 'data/media/icon/*.png', 'data/amir_migrate/*', 'data/amir_migrate/versions/*', 'data/weasyprint/*', 'data/weasyprint/*/*', 'data/weasyprint/*/*/*', 'data/cssselect2/*', 'data/cssselect2/*/*', 'data/pyphen/*', 'data/pyphen/*/*', 'data/tinycss2/*', 'data/tinycss2/*/*', 'data/webencodings/*']},
        keywords = 'amir accounting',
        scripts = ['scripts/amir'],
        data_files = data
        )


# Cleanup (remove /build, /mo, and *.pyc files:
print "Cleaning up..."
try:
    pass
    removeall("build/")
    os.rmdir("build/")
except:
    pass
try:
    pass
    removeall("locale/")
    os.rmdir("locale/")
except:
    pass
try:
    for f in os.listdir("."):
        if os.path.isfile(f):
            if os.path.splitext(os.path.basename(f))[1] == ".pyc":
                os.remove(f)
except:
    pass
