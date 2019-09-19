<style> .main-content{direction:rtl} </style>

نصب
---

نصب در لینوکس
=============

نصب در ubunutu با استفاده از مخزن شخصی
--------------------------------------

در صورتی که از Ubuntu 9.10 یا بالاتر استفاده می کنید می توانید با دستور زیر مخزن برنامه را به مخازن خود اضافه کنید و با استفاده از Pakage Manager آنرا نصب کنید با این کار بروز رسانی های بسته نیر می تواند به صورت خودکار انجام شود.

`sudo add-apt-repository ppa:hadi60/jooyeshgar`

در صورتی که از نسخه های قدیمی تر استفاده می کنید می توانید مخزن را به صورت دستی به لیست مخازن خود اضافه کنید

`deb [http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu](http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu "http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu") YOUR_UBUNTU_VERSION_HERE main deb-src [http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu](http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu "http://ppa.launchpad.net/hadi60/jooyeshgar/ubuntu") YOUR_UBUNTU_VERSION_HERE main`

برای اطلاعات بیشتر می توانید به آدرس زیر مراجعه کنید

[https://launchpad.net/~hadi60/+archive/jooyeshgar](https://launchpad.net/%7Ehadi60/+archive/jooyeshgar "https://launchpad.net/~hadi60/+archive/jooyeshgar")

نصب با استفاده از پکیج deb.
---------------------------

برای نصب از طریق پکیج کافی است آخرین نسخه را از [لانچپد](https://launchpad.net/amir "https://launchpad.net/amir") در یافت کنید و باکلیک کردن بر روی ان آنرا نصب کنید

نصب از طریق AUR در Archlinux
----------------------------

می توانید امیر را از  AUR در Archlinux نصب کنید.  PKGBUILD را می توانید از این جا دریافت کنید.

[https://aur.archlinux.org/packages/amir/](https://aur.archlinux.org/packages/amir/)

نصب با استفاده از کدهای منبع
----------------------------

در این روش تقریبا به نصب نیاز ندارید بعد از در یافت کدها کافی است از پوشه bin فایل amir را اجرا کنید

bin/amir

برطرف کردن وابستگی ها
---------------------

نرم‌افزار امیر به برنامه های زیر وابستگی دارد که ممکن است به صورت کامل توسط خود پکیج ها یا نرم‌افزار تشخیص داده نشود

*   [پایتون ۲.۵.۶](http://www.python.org/download/releases/2.6.5 "http://www.python.org/download/releases/2.6.5") (که به صورت پیش‌فرض بر روی اکثر دیستروها نصب است)
*   [SQLAlchemy](http://www.sqlalchemy.org/ "http://www.sqlalchemy.org") نسخه 0.6.0 یا بالاتر که بسته deb انرا از [اینجا](http://packages.debian.org/sid/python-sqlalchemy "http://packages.debian.org/sid/python-sqlalchemy") می توانید دریافت کنید.
*   [PyGTK](http://www.pygtk.org/ "http://www.pygtk.org") (نسخه‌های 2.16 به بعد) - کتابخانه pygtk برای تولید رابط گرافیکی برنامه استفاده می شود

نصب در ویندوز
=============

در حال حاضر به دو رش می توانید امیر را در ویندوز نصب کنید یکی با استفاده از فایل اینستالر و یکی هم با استفاده از کدهای منبع

نصب در ویندوز با استفاده از فایل اینستالر
-----------------------------------------

در ابتدا [فایل نصب را از اینجا](../download/Amir-0.1-win32-setup.exe "http://www.freeamir.com/download/Amir-0.1-win32-setup.exe") دریافت کنید و آنرا اجرا کنید

برنامه امیر برای اجرا به GTK 2.0 و فایل های کتابخانه ای ویژوال استدیو ۲۰۰۸ نیاز دارد در صورتی که برنامه ها را قبلا روی سیستم خود نصب نکرده اید در هنگام نصب می توانید آنها را برای نصب انتخاب کنید. فراموش نکنید در صورت حذف امیر از روی سیستم این نرم افزار ها حذف نخواهد شد و باید آنها را به صورت جدا گانه حذف کنید.

برای اجرا در ویندوز ۷ باید هم فایل اینستالر و هم فایل اجرای را باید با سطح دسترسی Administrator اجرا کنید.

نصب در ویندوز با استفاده از کدهای منبع
--------------------------------------

در ابتدا برای شروع باید بسته نصب کننده Python نسخه 2.6 را از[اینجا](http://python.org/download/ "http://python.org/download/") دریافت و نصب کنید .

  
سپس با دریافت بسته های زیر و نصب آنها سیستم خود را برای اجرای نرم افزار آماده میکنید . (برای راحتی کار می توانید نسخه های انتخاب شده را از [اینجا](../download/ "http://www.freeamir.com/download/") در یافت کنید.)

*   [pygobject](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pygobject/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pygobject/")
*   [PyGTK](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pygtk/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pygtk/")
*   [glade3](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/glade3/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/glade3/")
*   [setuptools](http://pypi.python.org/packages/2.5/s/setuptools/ "http://pypi.python.org/packages/2.5/s/setuptools/")
*   [PyCairo](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pycairo/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/pycairo/")
*   [GTK+](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/gtk+/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/gtk+/")
*   [intltools](http://ftp.acc.umu.se/pub/GNOME/binaries/win32/intltool/ "http://ftp.acc.umu.se/pub/GNOME/binaries/win32/intltool/")

نصب این بسته ها جهت اجرای این نرم افزار الزامی است . فقط توجه داشته باشید که حتما نسخه افزونه ای که دریافت میکنید با نسخه پایتون که نصب کرده یا میکنید یکسان باشد در غیر این صورت عملیات نصب و اجرای نرم افزار ناموفق خواهد بود .  
  
پس از نصب این افزونه ها شما باید مسیر نصب gtk+ را از طریق زیر در Path سیستم اضافه کنید . ( در صورتی که به صورت اتوماتیک اضافه نشده است )  
  

My Computer( Right click ) -> Properties - > Advanced ( tab ) -> Environment Variables

در پنجره باز شده در قسمت پایین ( System Variables ) متغیر Path را ویرایش و مسیر Gtk+ را در آن اضافه کنید . برای تاثیر گذاری این عملیات سیستم شمانیازمند راه اندازی مجدد است .  
  
بعد از راه اندازی مجدد میتوانید با استفاده از دستور زیر نرم افزار را اجرا کنید .

`c:\[**PYTHON_PATH**]\python.exe c:\amir\bin\amir`

در این مثال مسیر بازشده فایلهای نرم افزار در آدرس c:\\amir بوده است

  
* * *
