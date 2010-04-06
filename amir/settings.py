import pygtk
import gtk
import gobject

class Settings:
    datetypes = ["jalali", "gregorian"]
    datedelims = [":", "/", "-"]
    datefields = {"year":0, "month":1, "day":2}
    datetype = datetypes[0]
    datedelim = datedelims[1]
    
    def __init__(self):
        pass