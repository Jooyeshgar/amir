# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2010 <jooyeshgar> <info@jooyeshgar.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

# THIS IS Amir CONFIGURATION FILE
# YOU CAN PUT THERE SOME GLOBAL VALUE
# Do not touch until you know what you're doing.
# you're warned :)

# where your project will head for your data (for instance, images and ui files)
# by default, this is ../data, relative your trunk layout
__amir_data_directory__ = r'../data'
__license__ = 'GPL-3'


import os, optparse, logging, sys
from optparse import IndentedHelpFormatter
from share import share
import textwrap
import tempfile
import shutil
import ConfigParser
import platform

import database
    
## \defgroup Utility
## @{

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
            help_text  = self.expand_default(option)
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
    localelist = ["en_US", "fr", "he", "fa_IR", "tr"]
    langlist = ["English", "French", "Hebrew", "Persian", "Turkish"]
    directionlist = ["ltr", "ltr", "rtl", "rtl", "ltr"]
    
    datetypes = ["jalali", "gregorian"]
    datedelims = [":", "/", "-"]
    datefields = {"year":0, "month":1, "day":2}
    dateorders = [('year', 'month', 'day'), ('month', 'year', 'day'),
                  ('day', 'year', 'month'), ('year', 'day', 'month'),
                  ('day', 'month', 'year'), ('month', 'day', 'year')]
    
    def __init__(self):
        parser = optparse.OptionParser(version="%prog %ver",formatter=IndentedHelpFormatterWithNL() )
        parser.add_option("-v", "--verbose", action="store_const", const=1, dest="verbose", help="Show debug messages")
        parser.add_option("-n", "--noisy", action="store_const", const=2, dest="verbose", help="Show all debug messages")
        parser.add_option("-d", "--database", metavar="URL", action="store", dest="database", help="Set custom url for database (RFC-1738)\n\nExamples:\n\n-d sqlite:////absolute/path/to/foo.db\n\n-d sqlite:///:memory:\n\n-d mysql://user:pass@localhost/foo?charset=utf8")
        parser.add_option("-p", "--path", action="store", dest="pathname", help="Set data path")
        (self.options, self.args) = parser.parse_args()

        #set the logging level to show debug messages
        self.echodbresult = False
        if self.options.verbose:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug('logging enabled')
            if self.options.verbose == 2:
                self.echodbresult = True

	    # get pathname absolute or relative
        if self.options.pathname == None:
            if platform.system() == 'Windows':
                pathname = os.path.join(os.path.dirname(sys.executable),"data")
            elif __amir_data_directory__.startswith('..'):
                pathname = os.path.join(os.path.dirname(__file__) , __amir_data_directory__)
            else:
                pathname = __amir_data_directory__
            logging.debug('Project data directory. "%s"' % pathname)
        else:
            pathname = self.options.pathname

        abs_data_path = os.path.abspath(pathname)
        if os.path.exists(abs_data_path):
            self.data_path = abs_data_path
            if sys.platform == 'win32':
                self.locale_path = os.path.join(abs_data_path,"locale")
            else:
                self.locale_path = '/usr/share/locale'
        else:
            logging.error('Project path not found. "%s"' % abs_data_path)

        if platform.system() == 'Windows':
            confdir = os.path.join(os.path.expanduser('~'), 'amir')
        else:
            confdir = os.path.join(os.path.expanduser('~'), '.amir')

        if not os.path.exists(confdir):
            os.makedirs(confdir, 0755)

        confpath = os.path.join(confdir, 'amir.conf')
            
        dbfile = ''
        os.system.__subclasshook__
        logging.debug('Reading configuration "%s"' % confpath)
        
        #A ConfigParser is defined with default configuration values
        self.defaultConfig = {"current_database": "1", "repair_at_start": "no", "language": "C", "dateformat": "jalali", "delimiter": ":", 
                              "dateorder": "0", "use_latin_numbers": "yes", "name_font": "14", "header_font": "12",
                              "content_font": "9", "footer_font": "8", "paper_ppd_name": "A4", "paper_display_name": "A4",
                              "paper_width_points": "595", "paper_height_points": "841", "paper_orientation": "0", 
                              "top_margin": "18", "bottom_margin": "18", "right_margin": "18", "left_margin": "18"}
        self.sconfig = ConfigParser.SafeConfigParser(self.defaultConfig)

        if not os.path.exists(confpath):
            open(confpath, 'w').close()
 
        self.sconfig.readfp(open(confpath,'r+'))
        if not self.sconfig.has_section('General'):
            self.sconfig.add_section('General')
        if not self.sconfig.has_section('Report Fonts'):
            self.sconfig.add_section('Report Fonts')
        if not self.sconfig.has_section('Paper Setup'):
            self.sconfig.add_section('Paper Setup')
        

        self.dblist = []
        self.dbnames = []
        #NOTE: Current Db indice starts from 1 to be more readable for users
        #To access dblist and dbnames arrays, it should be subtracted by 1.
        self.currentdb = 1
        try:
            dblist = self.sconfig.get('General', 'databases')
            self.dblist = dblist.split(',')
            dbnames = self.sconfig.get('General', 'database_names')
            self.dbnames = dbnames.split(',')
            self.currentdb = self.sconfig.getint('General', 'current_database')
            dbfile = self.dblist[self.currentdb - 1]
        except ConfigParser.NoOptionError:
            dbfile = ''
        if self.options.database != None:
            dbfile = self.options.database
            self.dblist.append(dbfile)
            self.dbnames.append(os.path.basename(dbfile))
            
        if dbfile == '':
            dbfile = 'sqlite:///'+os.path.join(confdir, 'amir.sqlite')
            self.dblist.append(dbfile)
            self.dbnames.append('amir.sqlite')
            logging.error("No database path found. the default database %s will be opened for use." % dbfile)
            
        logging.info('database path: ' + dbfile)
        #try:
        self.db_repository = os.path.join(abs_data_path, 'amir_migrate')
        self.db = database.Database(dbfile, self.db_repository, self.echodbresult)
        share.session = self.db.session
        #except:
        #    sys.exit("Cannot open database.")
        
#        str = self.configfile.returnStringValue("repair_at_start")
        str = self.sconfig.get('General', 'repair_at_start')
        if str.lower() == 'yes':
            self.repair_atstart = True
        else:
            self.repair_atstart = False
            
#        str = self.configfile.returnStringValue("dateformat")
        str = self.sconfig.get('General', 'language')
        if str in self.localelist:
            self.locale = str
        else:
            self.locale = "en_US"
            
        str = self.sconfig.get('General', 'dateformat')
        if str == '':
            self.datetype = 0
        else:
            self.datetype = self.datetypes.index(str)
            
#        str = self.configfile.returnStringValue("delimiter")
        str = self.sconfig.get('General', 'delimiter')
        if str == '':
            self.datedelim = 0
        else:
            self.datedelim = self.datedelims.index(str)
            
#        str = self.configfile.returnStringValue("dateorder")
        str = self.sconfig.get('General', 'dateorder')
        if str == '':
            self.dateorder = 0
        else:
            self.dateorder = int(str)
            
        for i in range(0,3):
            field = self.dateorders[self.dateorder][i]
            self.datefields[field] = i
            
#        uselatin = self.configfile.returnStringValue("use_latin_numbers")
        uselatin = self.sconfig.get('General', 'use_latin_numbers')
        if uselatin.lower() == "no":
            self.digittype = 1  # 0 for latin, 1 for persian 
        else:
            self.digittype = 0
            
        self.namefont = self.sconfig.getint('Report Fonts', "name_font")
        self.headerfont = self.sconfig.getint('Report Fonts', "header_font")
        self.contentfont = self.sconfig.getint('Report Fonts', "content_font")
        self.footerfont = self.sconfig.getint('Report Fonts', "footer_font")
        
        self.paper_ppd = self.sconfig.get('Paper Setup', 'paper_ppd_name')
        self.paper_name = self.sconfig.get('Paper Setup', 'paper_display_name')
        self.paper_width = self.sconfig.getfloat('Paper Setup', 'paper_width_points')
        self.paper_height = self.sconfig.getfloat('Paper Setup', 'paper_height_points')
        self.paper_orientation = self.sconfig.getint('Paper Setup', 'paper_orientation')
        
        self.topmargin = self.sconfig.getint('Paper Setup', 'top_margin')
        self.botmargin = self.sconfig.getint('Paper Setup', 'bottom_margin')
        self.rightmargin = self.sconfig.getint('Paper Setup', 'right_margin')
        self.leftmargin = self.sconfig.getint('Paper Setup', 'left_margin')
        
    def updateConfigFile(self):
        if self.digittype == 1:
            uselatin = "no"
        else:
            uselatin = "yes"
            
        if self.repair_atstart == True:
            repair = "yes"
        else:
            repair = "no"
            
#        keys = ['database', 'dateformat', 'delimiter', 'dateorder', 'use_latin_numbers', 'repair_at_start',
#                'top_margin', 'bottom_margin', 'right_margin', 'left_margin',
#                'name_font', 'header_font', 'content_font', 'footer_font']
#        values = [self.db.dbfile, self.datetypes[self.datetype], self.datedelims[self.datedelim], str(self.dateorder), uselatin, repair,
#                  str(self.topmargin), str(self.botmargin), str(self.rightmargin), str(self.leftmargin),
#                  str(self.namefont), str(self.headerfont), str(self.contentfont), str(self.footerfont)]
#        self.sconfig.set('General', 'database', self.db.dbfile)
        self.sconfig.set('General', 'databases', ','.join(self.dblist))
        self.sconfig.set('General', 'database_names', ','.join(self.dbnames))
        self.sconfig.set('General', 'current_database', str(self.currentdb))
        self.sconfig.set('General', 'repair_at_start', repair)
        self.sconfig.set('General', 'language', self.locale)
        
        self.sconfig.set('General', 'dateformat', self.datetypes[self.datetype])
        self.sconfig.set('General', 'delimiter', self.datedelims[self.datedelim])
        self.sconfig.set('General', 'dateorder', str(self.dateorder))
        self.sconfig.set('General', 'use_latin_numbers', uselatin)
        
        self.sconfig.set('Report Fonts', 'name_font', str(self.namefont))
        self.sconfig.set('Report Fonts', 'header_font', str(self.headerfont))
        self.sconfig.set('Report Fonts', 'content_font', str(self.contentfont))
        self.sconfig.set('Report Fonts', 'footer_font', str(self.footerfont))
        
        self.sconfig.set('Paper Setup', 'paper_ppd_name', str(self.paper_ppd))
        self.sconfig.set('Paper Setup', 'paper_display_name', str(self.paper_name))
        self.sconfig.set('Paper Setup', 'paper_width_points', str(self.paper_width))
        self.sconfig.set('Paper Setup', 'paper_height_points', str(self.paper_height))
        self.sconfig.set('Paper Setup', 'paper_orientation', str(self.paper_orientation))
        
        self.sconfig.set('Paper Setup', 'top_margin', str(self.topmargin))
        self.sconfig.set('Paper Setup', 'bottom_margin', str(self.botmargin))
        self.sconfig.set('Paper Setup', 'right_margin', str(self.rightmargin))
        self.sconfig.set('Paper Setup', 'left_margin', str(self.leftmargin))
        
        if platform.system() == 'Windows':
            confdir = os.path.join(os.path.expanduser('~'), 'amir')
        else:
            confdir = os.path.join(os.path.expanduser('~'), '.amir')
        confpath = os.path.join(confdir, 'amir.conf')
        logging.debug('Writing configuration "%s"' % confpath)
        self.sconfig.write(open(confpath, 'wb'))
#        self.configfile.update(keys, values) 

    def restoreDefaultFonts(self):
        self.namefont = int(self.defaultConfig["name_font"])
        self.headerfont = int(self.defaultConfig["header_font"])
        self.contentfont = int(self.defaultConfig["content_font"])
        self.footerfont = int(self.defaultConfig["footer_font"])

## @}


