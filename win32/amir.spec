# -*- mode: python -*-
# changed for supporting GTK+3
block_cipher = None

# First we have to know where gtk is installed, we get this from registry
import _winreg
import msvcrt
k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'Software\\GTK3-Runtime Win64')
   
gtkdir = str(_winreg.QueryValueEx(k, 'InstallationDirectory')[0])
gtkversion = str(_winreg.QueryValueEx(k, 'BinVersion')[0])


#Then we want to go to the directory where the gtkrcfile is located

#gtkrc_dir = os.path.join('share', 'themes', 'MS-Windows', 'gtk-2.0')
gtkrc_dir1 = os.path.join('etc', 'gtk-3.0')
gtkrc_dir2 = os.path.join('share', 'themes', 'Default','gtk-3.0')
engines_dir = r'C:\\Program Files\\GTK3-Runtime Win64\\lib\\gdk-pixbuf-2.0\\2.10.0\\loaders'
#engines_dir = os.path.join('C:\Program Files\GTK3-Runtime Win64\'lib','gdk-pixbuf-2.0', '2.10.0' , 'loaders' )

gtkrc1 = os.path.join(gtkdir, gtkrc_dir1, 'settings.ini')
gtkrc2 = os.path.join(gtkdir, gtkrc_dir2, 'gtk-keys.css')
#wimp = os.path.join(gtkdir, engines_dir, 'libwimp.dll')
#wimp = os.path.join(gtkdir, engines_dir, t ) 
icon = '.\\amir.ico'
locale = '..\\locale\\'

a = Analysis(['..\\scripts\\amir'],
             pathex=['..\\scripts\\'],
             binaries=[(os.path.join( engines_dir , t),'GTK_lib') for t in  os.listdir(engines_dir) ],   #'GTK_lib'  will be name of the folder
             datas=[ ('..\\amir\\', 'amir\\'), ('C:\\Python27\\Lib\\site-packages\\sqlalchemy_migrate-0.11.0.dist-info\\', 'sqlalchemy_migrate-0.11.0.dist-info\\'), (gtkrc1, '.'), (gtkrc2, '.'), ('..\\locale\\', 'locale\\')],
             hiddenimports=['migrate.versioning.api', 'sqlalchemy.orm', 'sqlalchemy.ext.declarative'],
             hookspath=[],
             runtime_hooks=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='amir',
          icon=icon,
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='amir')
