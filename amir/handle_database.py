# handle_database.py

from  amir import amirconfig , database
from amir.share import share
from amir.database import *

def checkInputDb(inputfile):
	import sys
	import logging	
	from sqlalchemy import create_engine
	from sqlalchemy import MetaData, Table, Column, ForeignKey, ColumnDefault
	from sqlalchemy import exc		


	filetype = inputfile.split(".")[1]
	if filetype == "sql":
		type = "mysql://"		
	elif filetype == "sqlite":
		type= "sqlite:///"
	else :
		return -2


	try:
		engine = create_engine(type+inputfile, echo=True)
	except exc.DatabaseError:
		logging.error(sys.exc_info()[0])
		return -2

	return type

def backup(location):
	# from sqlalchemy.ext.serializer import loads, dumps
	# q = config.db.session.query(BankNames)
	# serialized_data = dumps(q.all())
	# file = open(location.get_filename() + "/backup.amir","w")
	# file.write(serialized_data)
	# file.close()

	dbFile = share.config.dbfile.split('///')
	file = open(dbFile[1], "r") 
	data = file.read()
	file = open(location.get_filename() + "/backup.amir","w")
	file.write(data)
	file.close()
	share.mainwin.silent_daialog(_("Backup saved successfully"))

def restore(location):
	# from sqlalchemy.ext.serializer import loads, dumps
	# file = open(location.get_filename(), "r") 
	# serialized_data = file.read()
	# restore_q = loads(serialized_data, config.db, config.db.session)
	# print restore_q
	# for x in restore_q:
	# 	config.db.session.merge(x)
	# config.db.session.commit()

	file = open(location.get_filename(), "r") 
	data = file.read()
	dbFile = share.config.dbfile.split('///')
	file = open(dbFile[1],"w")
	file.write(data)
	file.close()
	share.mainwin.silent_daialog(_("Backup restored successfully"))		

def createDb(dbName, builder):
	#creating new empty db	
	import os	
	from gi.repository import Gtk
	pathname = os.path.join(os.path.dirname(amirconfig.__file__) , amirconfig.__amir_data_directory__)			
	abs_data_path = os.path.abspath(pathname)
	db_repository = os.path.join(abs_data_path, 'amir_migrate')
	dbformat = "sqlite"
	dbType = "sqlite:///"
	from platform import system

	dbFile =dbType+os.path.join(share.config.confdir, dbName+"." + dbformat)
	try:		
		newdb = database.Database(dbFile, db_repository,share.config.echodbresult)
	except Exception as e:
		msg = _("There was a problem in creating new database. Maybe trying with another name will help...\n"+str(e))
		msgbox = Gtk.MessageDialog(builder.get_object("window1"),Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK , msg)
		msgbox.set_title(_("Error creating new database"))
		msgbox.run()	
		msgbox.destroy()
		return

	if builder.get_object("radiobutton2").get_active():
		################# filling db with importing ###########
		e = {
			"chkDoc" : 	(Bill , Notebook),
			"chkBank": 	(BankNames , BankAccounts),
			"chkConf": 	(Config,),
			"chkNote":	(Subject,),
			"chkFact":	(Factors,FactorItems),
			"chkUser":	(),
			"chkProductG":(ProductGroups,),
			"chkProduct": (Products,),
			"chkCust":	(Customers,),
			"chkCheq":	(Cheque,)
		}
		checkboxes = builder.get_object("grid5").get_children()	
		dbClasses = [] # permissions ...
		for checkbox in checkboxes:			
			if checkbox.get_active():
				a = Gtk.Buildable.get_name(checkbox) # widget ID	
				for clas in e[str(a)]:
					dbClasses .append(clas)	
		for clas in dbClasses:
			newdb.session.query(clas).delete()		
			movingData = share.config.db.session.query(clas).all()
			clas2 = clas.__table__							
			columns = clas2.columns.keys()							
			for d in movingData:
				data = dict( [(str(column), getattr(d, column)) for column in columns]   )								
				instant = clas(**data)
				newdb.session.add(instant)						
				# # 	or :			
				# moved = (clas2.delete())
				# newdb.session.execute(moved)		
				# print [c.name for c in clas2.columns]								
				# insert  = clas2.insert().from_select( [c.name for c in clas2.columns],clas2.select()) #select([c.name for c in config.db.session.clas]) )
				# newdb.session.execute(insert)
	newdb.session.commit()	

def detectDbType (filename):
	pass