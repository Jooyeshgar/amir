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

# THIS IS Amir CONFIGURATION FILE
# YOU CAN PUT THERE SOME GLOBAL VALUE
# Do not touch until you know what you're doing.
# you're warned :)

# where your project will head for your data (for instance, images and ui files)
# by default, this is ../data, relative your trunk layout
__amir_data_directory__ = r'/usr/share/amir'
__license__ = 'GPL-3'


import os, optparse, logging, sys
from optparse import IndentedHelpFormatter
import textwrap
import tempfile
import shutil

import database

class ConfigFile:
    def __init__(self, file):
        if not os.path.isfile(file):
            configdir = os.path.dirname(file)
            if not os.path.isdir(configdir):
                os.mkdir(configdir)
            hfile = open(file, 'a')
            hfile.close()
            logging.debug("Config file created. '%s'" % file)        
        self.filename = file
        
    def returnStringValue(self, key):
        file = open(self.filename, 'r')
        value = ''
        for line in file:
            if line.startswith(key + "="):
                value = line[len(key)+1 :]
                break
        file.close()
        return value.strip()
    
    def update(self, keys, values):
        input = open(self.filename, 'r')
        (outfile, outname) = tempfile.mkstemp()
        output = open(outname, 'w')
        for line in input:
            i = 0
            for key in keys:
                if line.startswith(key + "="):
                    line = key + "=" + values[i] + "\n"
                    del keys[i]
                    del values[i]
                    break
                i += 1
            output.write(line)
            
        # Insert keys not found in config file, at the end of output file   
        i = 0
        for key in keys:
            line = key + "=" + values[i] + "\n"
            i += 1
            output.write(line)
            
        input.close()
        output.close()
        
        os.remove(self.filename)
        shutil.move(outname, self.filename)
    
class IndentedHelpFormatterWithNL(IndentedHelpFormatter):
    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else: # start help on same line as opts
            opts = "%*s%-*s    " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            #help_text = option.help
            help_text = self.expand_default(option)
            help_lines = []
            #help_text = "\n".join([x.strip() for x in help_text.split("\n")])
            for para in help_text.split("\n\n"):
                help_lines.extend(textwrap.wrap(para, self.help_width))
                #if len(help_lines):
                #    help_lines[-1] += "\n"
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result) 
    
class AmirConfig:
    """Retrieve amir data path

    This path is by default <amir_lib_path>/../data/ in trunk
    and /usr/share/amir in an installed version but this path
    is specified at installation time.
    """
    data_path = ''
    #options = None
    datetypes = ["jalali", "gregorian"]
    datedelims = [":", "/", "-"]
    datefields = {"year":0, "month":1, "day":2}
    dateorders = [('year', 'month', 'day'), ('month', 'year', 'day'),
                  ('day', 'year', 'month'), ('year', 'day', 'month'),
                  ('day', 'month', 'year'), ('month', 'day', 'year')]
    
    def __init__(self):
    # get pathname absolute or relative
        if __amir_data_directory__.startswith('..'):
            pathname = os.path.join(os.path.dirname(__file__) , __amir_data_directory__)
        else:
            pathname = __amir_data_directory__
        
        abs_data_path = os.path.abspath(pathname)
        if os.path.exists(abs_data_path):
            self.data_path = abs_data_path
        else:
            logging.error('Project path not found. "%s"' % abs_data_path)
        
        parser = optparse.OptionParser(version="%prog %ver",formatter=IndentedHelpFormatterWithNL() )
        parser.add_option("-v", "--verbose", action="store_const", const=1, dest="verbose", help="Show debug messages")
        parser.add_option("-n", "--noisy", action="store_const", const=2, dest="verbose", help="Show all debug messages")
        parser.add_option("-d", "--database", metavar="URL", action="store", dest="database", help="Set custom url for database (RFC-1738)\n\nExamples:\n\n-d sqlite:////absolute/path/to/foo.db\n\n-d sqlite:///:memory:\n\n-d mysql://user:pass@localhost/foo")
        (self.options, self.args) = parser.parse_args()
        
        #set the logging level to show debug messages
        self.echodbresult = False
        if self.options.verbose:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug('logging enabled')
            if self.options.verbose == 2:
                self.echodbresult = True
            
        dbfile = ''
        confpath = os.path.join(os.path.expanduser('~'), '.amir', 'amir.conf')
        logging.debug('Reading configuration "%s"' % confpath)
        self.configfile = ConfigFile(confpath)
        
        if self.options.database != None:
            dbfile = self.options.database
        elif self.configfile.returnStringValue("database") == None:
            logging.error("Database registered in config file (%s) does not exist." % self.configfile.returnStringValue("database"))
        else :
            dbfile = self.configfile.returnStringValue("database")
            
        if dbfile == '':
            dbfile = os.path.join(os.path.expanduser('~'), '.amir', 'amir.sqlite')
            logging.error("No database path found. the default database %s will be opened for use." % dbfile)
            
        logging.info('database path: ' + dbfile)
        try:
            self.db = database.Database(dbfile, self.echodbresult)
        except:
            sys.exit("Cannot open database.")
        
        str = self.configfile.returnStringValue("dateformat")
        if str == '':
            self.datetype = 0
        else:
            self.datetype = self.datetypes.index(str)
            
        str = self.configfile.returnStringValue("delimiter")
        if str == '':
            self.datedelim = 0
        else:
            self.datedelim = self.datedelims.index(str)
            
        str = self.configfile.returnStringValue("dateorder")
        if str == '':
            self.dateorder = 0
        else:
            self.dateorder = int(str)
            
        for i in range(0,3):
            field = self.dateorders[self.dateorder][i]
            self.datefields[field] = i
            
        uselatin = self.configfile.returnStringValue("use_latin_numbers")
        if uselatin.lower() == "no":
            self.digittype = 1  # 0 for latin, 1 for persian 
        else:
            self.digittype = 0
        
    def updateConfigFile(self):
        if self.digittype == 1:
            uselatin = "no"
        else:
            uselatin = "yes"
        keys = ['database', 'dateformat', 'delimiter', 'dateorder', 'use_latin_numbers']
        values = [self.db.dbfile, self.datetypes[self.datetype], self.datedelims[self.datedelim], str(self.dateorder), uselatin]
        self.configfile.update(keys, values) 
try:
    config
except NameError:
    config = AmirConfig()

