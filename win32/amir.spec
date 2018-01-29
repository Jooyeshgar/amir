# -*- mode: python -*-

block_cipher = None

# First we have to know where gtk is installed, we get this from registry
import _winreg
import msvcrt
try:
    k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'Software\\GTK2-Runtime')
except EnvironmentError:
    print 'You must install the Gtk+ 2.2 Runtime Environment to run this program'
    while not msvcrt.kbhit():
        pass
    sys.exit(1)
else:    
    gtkdir = str(_winreg.QueryValueEx(k, 'InstallationDirectory')[0])
    gtkversion = str(_winreg.QueryValueEx(k, 'BinVersion')[0])


#Then we want to go to the directory where the gtkrcfile is located
gtkrc_dir = os.path.join('share', 'themes', 'MS-Windows', 'gtk-2.0')
engines_dir = r'lib\\gtk-2.0\\2.10.0\\engines'

gtkrc = os.path.join(gtkdir, gtkrc_dir, 'gtkrc')
wimp = os.path.join(gtkdir, engines_dir, 'libwimp.dll')
icon = '.\\amir.ico'
locale = '..\\locale\\'

a = Analysis(['..\\scripts\\amir'],
             pathex=['..\\scripts\\'],
             binaries=[(wimp, os.path.join(engines_dir))],
             datas=[ ('..\\amir\\', 'amir\\'), ('C:\\Python27\\Lib\\site-packages\\sqlalchemy_migrate-0.11.0.dist-info\\', 'sqlalchemy_migrate-0.11.0.dist-info\\'), (gtkrc, '.'), ('..\\locale\\', 'locale\\')],
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
