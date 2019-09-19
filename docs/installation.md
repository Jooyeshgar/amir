Installation
------------

  

Installation on Linux
=====================

  

Install Nightly Builds (Recommended)
------------------------------------

Install Bazaar version control system ([follow this link](http://wiki.bazaar.canonical.com/Download)) and _python-migrate_ package, then copy a local branch for yourself from using the following command.

bzr branch lp:amir

In this way, you do not need to install the code, just run Amir from the bin folder.

bin/amir

Ubunutu installation using a personal repository
------------------------------------------------

Ubuntu 9.10 or higher can use personal repositories and you can install Amir using the Pakage Manager

you can use this command to add amir to your repository

sudo add-apt-repository ppa:hadi60/jooyeshgar

  

If you use the older version, you can manually add repository to your repository list

deb [http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu](http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu "http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu") YOUR\_UBUNTU\_VERSION\_HERE main deb-src [http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu](http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu "http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu") YOUR\_UBUNTU\_VERSION\_HERE main

For more information, see [https://launchpad.net/~hadi60/+archive/jooyeshgar](https://launchpad.net/~hadi60/+archive/jooyeshgar)

Install from Archlinux AUR
--------------------------

You can use AUR to install Amir in Archlinux. Here is the link to AUR PKGBUILD of Amir, [https://aur.archlinux.org/packages/amir/](https://aur.archlinux.org/packages/amir/)

Package Installation Using .deb File
------------------------------------

To install the latest version of the package you can [download it from Lanchpad](https://launchpad.net/amir) and install it.

  

To resolve dependencies
-----------------------

Amir depends on the following packages that must be installed before using Amir.

*   [Python 2.5.6](http://www.python.org/download/releases/2.6.5/) (which is installed by default on most distro)
*   [SQLAlchemy](http://www.sqlalchemy.org/) 0.6.0 or higher
*   [Pygtk](http://www.pygtk.org/) (Version 2.16 or higher)
*   [SQLAlchemy-migrate](http://code.google.com/p/sqlalchemy-migrate/)

Installation on Windows
=======================

  

Download [Windows installation file and run it.](../download/Amir-0.1-win32-setup.exe)

For installing on Windows 7 installer and executable file should be run with Administrator privileges.
