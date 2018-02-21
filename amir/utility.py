#-*- encoding: utf-8 -*-

from share import share


## \defgroup Utility
## @{

# TODO: Instead of using just persian characters,
# TODO: chek mee 
## Check the active locale and choose number characters from that locale
def LN (num, comma=True):
    
    if type(num) == int:
        num = str(num)
    elif type(num) == float:
        num = str(num)
        if num[-2:]==".0":
            num = num[:-2]   

    if comma:
        s = num
        dot_pos = s.find('.')
        if dot_pos != -1:
            s = s[:dot_pos]
            
        l = [x for x in s]
        for x in reversed(range(len(s))[::3]):
            l.insert(-x, ',')
        l = ''.join(l[1:])
        
        if dot_pos != -1:
            num = l + num[dot_pos:]
        else:
            num = l
        
    if share.config.digittype == 1:
        num = convertToPersian(num)
    return num

def getFloatNumber (number_string):
    """
        Reverses LN() procedure. Gets a string representing a number,
        (Maybe containing commas) And returns the value as float
        Backward compatible dont use it
    """
    if not number_string:
        return 0
        
    number_string = number_string.replace(',', '')
    number_string = convertToLatin(number_string)
    return float(number_string)

def getFloat (number_string):
    """
        Reverses LN() procedure. Gets a string representing a number,
        (Maybe containing commas) And returns the value as float
    """
    if not number_string:
        return 0
        
    number_string = number_string.replace(',', '')
    number_string = convertToLatin(number_string)
    return float(number_string)
        
def getInt (number_string):
    """
        Reverses LN() procedure. Gets a string representing a number,
        (Maybe containing commas) And returns the value as integer
    """
    if not number_string:
        return 0
        
    number_string = number_string.replace(',', '')
    number_string = convertToLatin(number_string)
    return int(number_string)
    
def readNumber (number):
    return number.replace('0123456789', u'۰۱۲۳۴۵۶۷۸۹')

def convertToLatin (input_string):
    """
        Searchs for farsi digits in input_string and converts them to latin ones.
    """
    en_numbers = '0123456789.%'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹/٪'
    output_string = u''
    for c in unicode(input_string):
        if c in unicode(fa_numbers):
            c = en_numbers[fa_numbers.index(c)]
        output_string += c
        
    return output_string

def convertToPersian (input_string):
    """
        Searchs for latin digits in input_string and converts them to persian ones.
    """
    
    en_numbers = '0123456789.%'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹/٪'
    
    output_string = u''
    for c in unicode(input_string):
        if c in en_numbers:
            c = fa_numbers[en_numbers.index(c)]
        output_string += c
        
    return output_string

# Localize number base on config file   
#def LN(num):
#    if type(num) == int:
#        num = str(num)
#    elif type(num) == float:
#        num = str(num)
#        if num[-2:]==".0":
#           num = num[:-2]       
#    if config.digittype == 1:
#        return convertToPersian(num)
#    return num

def is_numeric(var):
    try:
        float(readNumber(var))
        return True
    except ValueError:
        return False

## @}
