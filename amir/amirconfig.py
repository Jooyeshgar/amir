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
__amir_data_directory__ = '../data/'


import os,optparse,logging
from optparse import IndentedHelpFormatter
import textwrap
import database

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
    
    def __init__(self):
    # get pathname absolute or relative
        if __amir_data_directory__.startswith('/'):
            pathname = __amir_data_directory__
        else:
            pathname = os.path.dirname(__file__) + '/' + __amir_data_directory__
        
        abs_data_path = os.path.abspath(pathname)
        if os.path.exists(abs_data_path):
            self.data_path = abs_data_path
        else:
            logging.error('project path not found')
        
        parser = optparse.OptionParser(version="%prog %ver",formatter=IndentedHelpFormatterWithNL() )
        parser.add_option("-v", "--verbose", action="store_const", const=1, dest="verbose", help="Show debug messages")
        parser.add_option("-n", "--noisy", action="store_const", const=2, dest="verbose", help="Show all debug messages")
        parser.add_option("-d", "--database", metavar="URL", action="store", dest="database", help="Set custom url for database (RFC-1738)\n\nExamples:\n\n-d sqlite:////absolute/path/to/foo.db\n\n-d sqlite:///:memory:\n\n-d mysql://user:pass@localhost/foo")
        (self.options, self.args) = parser.parse_args()
        
        #set the logging level to show debug messages
        if self.options.verbose:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug('logging enabled')
            
        if self.options.database == None:
            self.db = database.Database()
        else:
            self.db = database.Database(self.options.database)
        
        
try:
    config
except NameError:
    config = AmirConfig()

