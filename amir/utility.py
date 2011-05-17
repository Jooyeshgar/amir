#-*- encoding: utf-8 -*-

from amirconfig import config

#===============================================================================
# TODO: Instead of using just persian characters, 
# Check the active locale and choose number characters from that locale
#===============================================================================
def showNumber (number, comma=True):
	s = str(number)

	if comma:
		#l = [x for x in s if x in '1234567890']
		dot_pos = s.find('.')
		if dot_pos != -1:
			s = s[:dot_pos]
			
		l = [x for x in s]
		for x in reversed(range(len(s))[::3]):
			l.insert(-x, ',')
		l = ''.join(l[1:])
		
		if dot_pos != -1:
			l += str(number)[dot_pos:]
        
        
        
    #NOTE this doesn't replace characters one by one, it replaces the whole string.
    #     reverted to previous form.
    #if config.digittype == 1:
        #s.replace(u'۰۱۲۳۴۵۶۷۸۹','0123456789')
	if config.digittype == 1:
	    l = convertToPersian(l)
	return l

def readNumber (number):
    return number.replace('0123456789', u'۰۱۲۳۴۵۶۷۸۹')

def convertToLatin (input_string):
    """
        Searchs for farsi digits in input_string and converts them to latin ones.
    """
    en_numbers = '0123456789.'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹/'
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
    en_numbers = '0123456789.'
    fa_numbers = u'۰۱۲۳۴۵۶۷۸۹/'
    
    output_string = u''
    for c in unicode(input_string):
        if c in en_numbers:
            c = fa_numbers[en_numbers.index(c)]
        output_string += c
        
    return output_string

def is_numeric(var):
    try:
        float(readNumber(var))
        return True
    except ValueError:
        return False

