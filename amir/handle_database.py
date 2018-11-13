# handle_database.py

from amir import amirconfig, database
from amir.share import share
from sqlalchemy import *
from amir.database import *
import database
import os

def checkInputDb(inputfile, selectedFormat):
    import os, sys
    import logging
    from sqlalchemy import create_engine
    from sqlalchemy import MetaData, Table, Column, ForeignKey, ColumnDefault
    from sqlalchemy import exc

    dbtypes = (("sqlite", "sqlite:///"),
               ("sql", "mysql://"))  # mysql won't be used in this function. It is just for filling dbTypes !
    filename = ""
    if selectedFormat != 1:

        filename = os.path.split(inputfile)  # filename = ( 'directory' , 'file.format')
        splitByDot = filename[1].split(".")
        l = len(splitByDot)
        if l > 1:  # if file name is with format (e.g .sqlite)
            filetype = splitByDot[l - 1]
            if filetype == dbtypes[selectedFormat][0]:
                type = dbtypes[selectedFormat][1]
                filename = filename[1]
            else:
                return -1
        else:  # if filename is without any format
            filetype = dbtypes[selectedFormat][0]
            type = dbtypes[selectedFormat][1]
            inputfile += "." + filetype
            filename = filename[1] + "." + filetype

        if not os.path.isfile(inputfile):
            return filename
    try:
        #engine = create_engine(type + inputfile, echo=True)
        database.Database(inputfile, share.config.db_repository, share.config.echodbresult)
    except exc.DatabaseError:
        logging.debug(sys.exc_info()[0])
        return -2

    return filename


def backup1(location):
    from datetime import date
    import json
    a = (Bill,Config, Notebook,BankNames, BankAccounts,ProductGroups, Products,Users, Permissions, Subject, Factors, FactorItems,CustGroups, Customers, Cheque, ChequeHistory)
    currentDbName = (share.config.dbnames[share.config.currentdb - 1]).split(".")
    currentDbName = ''.join(str(e) for e in currentDbName[:len(currentDbName)-1] )
    year = date.today().year
    newName = currentDbName+str(year)
    data = {"basic": {"Your company":"Jooyeshgar" },"info":{"user":"root","time":"17:38"}, "table":[]}

    for aa in a :
        arrayData = []
        q = share.config.db.session.query(aa)
        all = q.all()

        for row in all :
            jsonn = row2dict(row)
            arrayData.append(jsonn)

        data['table'].append({"name":str(aa.__name__), "rows": arrayData } )
    file = open(os.path.join(location.get_filename() ,newName+".amirbkp"),"w")
    dump = json.dumps(data )
    file.write(dump)
    file.close()
    share.mainwin.silent_daialog(_("Backup saved successfully"))
    return

import zipfile
def backup(location):
    from sqlalchemy.ext.serializer import  dumps
    from datetime import date
    year = date.today().year
    currentDbName = (share.config.dbnames[share.config.currentdb - 1]).split(".")
    currentDbName = ''.join(str(e) for e in currentDbName[:len(currentDbName) - 1])
    newName = currentDbName + str(year)
    dir = os.path.join(location.get_filename(), newName )
    os.mkdir(dir)
    tables = (Bill, Config, Notebook, BankNames, BankAccounts, ProductGroups, Products, Users, Permissions, Subject, Factors,
         FactorItems, CustGroups, Customers, Cheque, ChequeHistory)
    serialized_data = ""
    for table in tables :
        arrayData = []
        q = share.config.db.session.query(table)
        all = q.all()
        serialized_data = dumps(all)
        file = open(dir +"/" + str(table.__name__),"w")
        file.write(serialized_data)
        file.close()

    print location.get_filename()
    from shutil import make_archive
    make_archive(
        dir,
        'zip',  # the archive format - or tar, bztar, gztar
        location.get_filename(),  # root for archive - current working dir if None
        base_dir=newName)

    for table in tables:
        os.remove(os.path.join(dir,table.__name__))
    os.rmdir(dir)

    share.mainwin.silent_daialog(_("Backup saved successfully"))

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = unicode(getattr(row, column.name))

    return d

def restore(location):
    # import json
    # file = open(location.get_filename(), "r")
    # data = json.load(file)
    # tables = data['table']
    # for t in tables:
    #     #     name  = t['name']
    #     #     rows = t['rows']
    #     #     for row in rows:

    import zipfile

    zip_ref = zipfile.ZipFile(location.get_filename(), 'r')
    zip_ref.extractall(location.get_filename().split(".zip")[0])
    zip_ref.close()
    return
    from sqlalchemy.ext.serializer import loads

    metadata = MetaData(share.config.db.engine)
    folder =  os.path.dirname(location.get_filename())
    a = ( Bill, Config, Notebook, BankNames, BankAccounts, ProductGroups, Products, Users, Permissions, Subject, Factors,
          CustGroups, Customers, Cheque, ChequeHistory )
    for table in a :
        file = open(location.get_filename().split(".zip")[0]+ "/"+ str(table.__name__), "r")
        serialized_data = file.read()
        restore_q = loads(serialized_data,  metadata, share.config.db.session)
     #   share.config.db.session.query(table).delete()
        for row in restore_q:
            share.config.db.session.merge(row)

        share.config.db.session.commit()
        file.close()
    share.mainwin.silent_daialog(_("Backup restored successfully"))


def createDb(dbName, builder):
    # creating new empty db
    from gi.repository import Gtk
    pathname = os.path.join(os.path.dirname(amirconfig.__file__), amirconfig.__amir_data_directory__)
    abs_data_path = os.path.abspath(pathname)
    db_repository = os.path.join(abs_data_path, 'amir_migrate')
    dbformat = "sqlite"
    dbType = "sqlite:///"
    from platform import system

    fileaddress= os.path.join(share.config.confdir, dbName + "." + dbformat)
    dbFile = dbType + fileaddress
    try:
        newdb = database.Database(dbFile, db_repository, share.config.echodbresult)
    except Exception as e:
        msg = _("There was a problem in creating new database. Maybe trying with another name will help...\n" + str(e))
        msgbox = Gtk.MessageDialog(builder.get_object("window1"), Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, msg)
        msgbox.set_title(_("Error creating new database"))
        msgbox.run()
        msgbox.destroy()
        return

    if builder.get_object("radiobutton2").get_active():
        ################# filling db with importing ###########
        e = {
            "chkDoc": (Bill, Notebook),
            "chkBank": (BankNames, BankAccounts),
            "chkConf": (Config,),
            "chkNote": (Subject,),
            "chkFact": (Factors, FactorItems),
            "chkUser": (),
            "chkProductG": (ProductGroups,),
            "chkProduct": (Products,),
            "chkCust": (Customers,),
            "chkCheq": (Cheque,)
        }
        checkboxes = builder.get_object("grid5").get_children()
        dbClasses = []  # permissions ...
        for checkbox in checkboxes:
            if checkbox.get_active():
                a = Gtk.Buildable.get_name(checkbox)  # widget ID
                for clas in e[str(a)]:
                    dbClasses.append(clas)
        for clas in dbClasses:
            newdb.session.query(clas).delete()
            movingData = share.config.db.session.query(clas).all()
            clas2 = clas.__table__
            columns = clas2.columns.keys()
            for d in movingData:
                data = dict([(str(column), getattr(d, column)) for column in columns])
                instant = clas(**data)
                newdb.session.add(instant)
            # # 	or :
            # moved = (clas2.delete())
            # newdb.session.execute(moved)
            # print [c.name for c in clas2.columns]
            # insert  = clas2.insert().from_select( [c.name for c in clas2.columns],clas2.select()) #select([c.name for c in config.db.session.clas]) )
            # newdb.session.execute(insert)
    newdb.session.commit()

def detectDbType( fullname):
    format = fullname.split("/")[0]
    format = format.split(":")[0]
    return format

def showDBdetails(fullname):
    pieces =  fullname.split("/")
    format =pieces[0]
    if format == "mysql:":
        lastPart = pieces[len(pieces)-1]
        lastPart = lastPart.split("?")[0]
        return lastPart
    if format == "sqlite:":
        return fullname[10:]

def clean():
    pass
