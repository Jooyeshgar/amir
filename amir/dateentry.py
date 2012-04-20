import pygtk
import gtk
import gobject
import string
from datetime import date

from utility import LN,getInt
from share import share
from calverter import calverter

## \defgroup Utility
## @{

def dateToString(date):
    if share.config.datetypes[share.config.datetype] == "jalali":
        jd = DateEntry.cal.gregorian_to_jd(date.year, date.month, date.day)
        (year, month, day) = DateEntry.cal.jd_to_jalali(jd)
    else:
        (year, month, day) = (date.year, date.month, date.day)
        
    datelist = ["", "", ""]
    datelist[share.config.datefields["year"]] = year
    datelist[share.config.datefields["month"]] = month
    datelist[share.config.datefields["day"]] = day
        
    delim = share.config.datedelims[share.config.datedelim]
    datestring = str(datelist[0]) + delim + str(datelist[1]) + delim + str(datelist[2])
    datestring = LN(datestring)
    return datestring

def stringToDate(dateString):
    delim = share.config.datedelims[share.config.datedelim]
    dateList = dateString.split(delim)
    if len(dateList) != 3:
        print "Error in the date string format!"
        pass
    else:
        dy = dateList[0]
        dm = dateList[1]
        dd = dateList[2]
        dateObj = date(int(dy),int(dm),int(dd))
        return dateObj 

## @}
    
## \defgroup Widgets
## @{

class DateEntry(gtk.Entry):
    
    cal = calverter()
    
    def __init__(self, init_date=None):
        """
        date is a tuple containing the default DateEntry value. date is in the form of (YYYY, MM, DD) as three integers. 
        """
        gtk.Entry.__init__(self)
        self.set_alignment(0.5)
        self.connect("focus-out-event", self.correctDate)
#        self.connect("hide", self.correctDate)
        
        self.cal = calverter()

        if init_date != None:
            (self.year, self.month, self.day) = init_date
        else:
            today = date.today()
            if share.config.datetypes[share.config.datetype] == "jalali":
                jd = self.cal.gregorian_to_jd (today.year, today.month, today.day)
                jalali = self.cal.jd_to_jalali(jd)
                (self.year, self.month, self.day) = jalali
            else:
                self.year = today.year
                self.month = today.month
                self.day = today.day
                
        self.showDate(self.year, self.month, self.day)
        
    def showDate(self, year, month, day):
        datelist = ["", "", ""]
        datelist[share.config.datefields["year"]] = year
        datelist[share.config.datefields["month"]] = month
        datelist[share.config.datefields["day"]] = day
        
        delim = share.config.datedelims[share.config.datedelim]
        datestring = str(datelist[0]) + delim + str(datelist[1]) + delim + str(datelist[2])
        datestring = LN(datestring)
        self.set_text(datestring)
        self.year = year
        self.month = month
        self.day = day
        
    #Assuming that date objects show gregorian date.
    def showDateObject(self, date):
        if share.config.datetypes[share.config.datetype] == "jalali":
            jd = self.cal.gregorian_to_jd(date.year, date.month, date.day)
            (jyear, jmonth, jday) = self.cal.jd_to_jalali(jd)
            self.showDate(jyear, jmonth, jday)
        else:
            self.showDate(date.year, date.month, date.day)
        
    def getDateObject(self):
        if share.config.datetypes[share.config.datetype] == "jalali":
            jd = self.cal.jalali_to_jd(self.year, self.month, self.day)
            (gyear, gmonth, gday) = self.cal.jd_to_gregorian(jd)
            return date(gyear, gmonth, gday)
        else :
            return date(self.year, self.month, self.day)
        
    def correctDate(self, sender, event):
        text = self.get_text()
        datelist = string.split(text, share.config.datedelims[share.config.datedelim]) 
        try:
            tyear = datelist[share.config.datefields["year"]]
            tyear = getInt(tyear)
        except IndexError:
            tyear = ""
        try:
            tmonth = datelist[share.config.datefields["month"]]
            tmonth = getInt(tmonth)
        except IndexError:
            tmonth = ""
        try:
            tday = datelist[share.config.datefields["day"]]
            tday = getInt(tday)
        except IndexError:
            tday = ""
        
        if config.datetypes[config.datetype] == "jalali":
            minyear = 1349
            baseyear = "1300"
        else:
            minyear = 1970
            baseyear = "2000"
            
        try:
            if len(tyear) > 4:
                year = self.year
            else:
                year = int(baseyear[:4-len(tyear)] + tyear)
                
            if year < minyear:
                year = minyear
        except ValueError:
            year = minyear
            
        try:
            month = int(tmonth)
            if month > 12:
                month = 12
            else:
                if month < 1:
                    month = 1
        except ValueError:
            month = 1
            
        try:
            day = int(tday)
            if day > 31:
                day = 31
            else:
                if day < 1:
                    day = 1
        except ValueError:
            day = 1
                
        if config.datetypes[config.datetype] == "jalali":
            jd = self.cal.jalali_to_jd(year, month, day)
            (gyear, gmonth, gday) = self.cal.jd_to_gregorian(jd)
        else:
            (gyear, gmonth, gday) = (year, month, day)
            
        correct = 0
        while correct == 0:
            try:
                testdate = date(gyear, gmonth, gday)
                correct = 1
            except ValueError:
                gday -= 1
                day -= 1
                
        self.showDate(year, month, day)
        self.year = year
        self.month = month
        self.day = day

## @}
