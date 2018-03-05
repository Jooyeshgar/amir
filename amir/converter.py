
# Gregorian & Jalali ( Hijri_Shamsi , Solar ) Date Converter Functions
# Author: JDF.SCR.IR =>> Download Full Version : http://jdf.scr.ir/jdf
# License: GNU/LGPL _ Open Source & Free _ Version: 2.72 : [2017=1396]
# --------------------------------------------------------------------
# 1461 = 365*4 + 4/4   &  146097 = 365*400 + 400/4 - 400/100 + 400/400
# 12053 = 365*33 + 32/4      &       36524 = 365*100 + 100/4 - 100/100


def gregorian_to_jalali(gy,gm,gd):
 g_d_m=[0,31,59,90,120,151,181,212,243,273,304,334]
 if(gy>1600):
  jy=979
  gy-=1600
 else:
  jy=0
  gy-=621
 if(gm>2):
  gy2=gy+1
 else:
  gy2=gy
 days=(365*gy) +(int((gy2+3)/4)) -(int((gy2+99)/100)) +(int((gy2+399)/400)) -80 +gd +g_d_m[gm-1]
 jy+=33*(int(days/12053))
 days%=12053
 jy+=4*(int(days/1461))
 days%=1461
 if(days > 365):
  jy+=int((days-1)/365)
  days=(days-1)%365
 if(days < 186):
  jm=1+int(days/31)
  jd=1+(days%31)
 else:
  jm=7+int((days-186)/30)
  jd=1+((days-186)%30)
 return [jy,jm,jd]


def jalali_to_gregorian(jy,jm,jd):
 if(jy>979):
  gy=1600
  jy-=979
 else:
  gy=621
 if(jm<7):
  days=(jm-1)*31
 else:
  days=((jm-7)*30)+186
 days+=(365*jy) +((int(jy/33))*8) +(int(((jy%33)+3)/4)) +78 +jd
 gy+=400*(int(days/146097))
 days%=146097
 if(days > 36524):
  gy+=100*(int(--days/36524))
  days%=36524
  if(days >= 365):
   days+=1
 gy+=4*(int(days/1461))
 days%=1461
 if(days > 365):
  gy+=int((days-1)/365)
  days=(days-1)%365
 gd=days+1
 if((gy%4==0 and gy%100!=0) or (gy%400==0)):
  kab=29
 else:
  kab=28
 sal_a=[0,31,kab,31,30,31,30,31,31,30,31,30,31]
 gm=0
 while(gm<13):
  v=sal_a[gm]
  if(gd <= v):
   break
  gd-=v
  gm+=1
 return [gy,gm,gd]


