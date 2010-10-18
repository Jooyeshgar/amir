###******************************************************************************
###   
###    Amir Accounting Application
###   
###    Open Source accounting application, mainly designed for persian users.
###   
###    Warehousing Application:
###        Started on:            October 2010
###        Company:               Jouyeshgar Rayaneh, Isfahan, Iran 
###        Coding by:             Riyaz Mogharabin
###   
###*****************************************************************************
#
##-----------------------------------------------------------------------
## Importing needed packages
##-----------------------------------------------------------------------
#import  numberentry
#import  subjects
#import  products
#import  gobject
#import  groups
#import  pygtk
#import  gtk
#
#from    helpers                 import      get_builder
#from    sqlalchemy.orm.util     import      outerjoin
#from    amirconfig              import      config
#from    datetime                import      date
#from    database                import      *
#
####################################################################################
###
### Class GroupsProducts:    Displays all the warehousing registered products. 
###
####################################################################################
#