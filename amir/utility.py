#-*- encoding: utf-8 -*-

from amirconfig import config

#===============================================================================
# TODO: Instead of using just persian characters, 
# Check the active locale and choose number characters from that locale
#===============================================================================
def showNumber (number):
    s = str(number)
    l = [x for x in s if x in '1234567890']
    for x in reversed(range(len(s))[::3]):
        l.insert(-x, ',')
    l = ''.join(l[1:])
    
    if config.digittype == 1:
        l = convertToPersian(l)
    return l

def convertToLatin (input_string):
    """
        Searchs for farsi digits in input_string and converts them to latin ones.
    """
    en_numbers = '0123456789'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹'
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
    en_numbers = '0123456789'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹'
    
    output_string = u''
    for c in unicode(input_string):
        if c in en_numbers:
            c = fa_numbers[en_numbers.index(c)]
        output_string += c
        
    return output_string
