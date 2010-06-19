#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010 <jooyeshgar> <info@jooyeshgar.com>
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, 'To build amir you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)

assert DistUtilsExtra.auto.__version__ >= '2.10', 'needs DistUtilsExtra.auto >= 2.10'
import os
import sys
import shutil
from glob import glob

def update_data_path(prefix, oldvalue=None):

    try:
        #fin = file('amir/amirconfig.py', 'r')
        #fout = file(fin.name + '.new', 'w')
        fin = open(os.path.join(os.path.dirname(__file__), "amir", "amirconfig.py"), 'r')
        fout = open(os.path.join(os.path.dirname(__file__), "amir", "amirconfig.py.new"), 'w')

        for line in fin:            
            fields = line.split(' = ') # Separate variable from value
            if fields[0] == '__amir_data_directory__':
                # update to prefix, store oldvalue
                if not oldvalue:
                    oldvalue = fields[1]
                    line = "%s = r'%s'\n" % (fields[0], prefix)
                else: # restore oldvalue
                    line = "%s = %s" % (fields[0], oldvalue)
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        
        configname = fin.name
        os.remove(fin.name)
        shutil.move(fout.name, configname)
    except (OSError, IOError):
        print ("ERROR: Can't find amir/amirconfig.py")
        sys.exit(1)
    return oldvalue


def update_desktop_file(datadir):

    try:
        #fin = file('amir.desktop.in', 'r')
        #fout = file(fin.name + '.new', 'w')
        fin = open(os.path.join(os.path.dirname(__file__), "amir.desktop.in"), 'r')
        fout = open(os.path.join(os.path.dirname(__file__), "amir.desktop.in.new"), 'w')

        for line in fin:            
            if 'Icon=' in line:
                line = "Icon=%s\n" % (os.path.join(datadir, 'media', 'icon.png'))
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        
        desktopname = fin.name
        os.remove(fin.name)
        shutil.move(fout.name, desktopname)
    except (OSError, IOError):
        print ("ERROR: Can't find amir.desktop.in")
        sys.exit(1)


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        if self.root or self.home:
            print "WARNING: You don't use a standard --prefix installation, take care that you eventually " \
            "need to update quickly/quicklyconfig.py file to adjust __quickly_data_directory__. You can " \
            "ignore this warning if you are packaging and uses --prefix."
        previous_value = update_data_path(os.path.join(self.prefix, 'share', 'amir'))
        update_desktop_file(os.path.join(self.prefix, 'share', 'amir'))
        DistUtilsExtra.auto.install_auto.run(self)
        #update_data_path(self.prefix, previous_value)


        
##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='amir',
    version='0.1',
    license='GPL-3',
    author='jooyeshgar',
    author_email='info@jooyeshgar.com',
    description='Amir accounting software',
    long_description='Just another accounting software for persian',
    url='https://launchpad.net/amir',
    
    packages=['amir'],
    data_files = [
        ('share/applications', ['amir.desktop.in']),
        
        ('share/amir/media', glob('data/media/*.png') ),
        ('share/amir/media/icon', glob('data/media/icon/*.png') ),
        ('share/amir/ui', glob('data/ui/*.*') ),
      ],
    extra = {
        "windows" : [{
        'script' : 'bin/amir',
        }],
    },
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )
