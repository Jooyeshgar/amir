;--------------------------------
;Global Variables

Var GTK_FOLDER
Var GTK_INSTALL_HINT

;--------------------------------
;Defines

!define icon "amir.ico"
!define PROGRAM_NAME "Amir"
!define PROGRAM_VERSION "0.1"
!define PROGRAM_WEB_SITE "http://www.freeamir.com"
!define AMIR_INSTALLER_VERSION "0.1"


!define GTK_MIN_VERSION				"2.16.0"
!define GTK_REG_KEY				"SOFTWARE\GTK\2.0"

;--------------------------------
;Include Modern UI

!include "MUI2.nsh"

# Installer
!define MUI_ICON "amir.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP "installer-top.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer-side.bmp"
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_ABORTWARNING

# Uninstaller
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_HEADERIMAGE_UNBITMAP "installer-top.bmp"
!define MUI_WELCOMEFINISHPAGE_UNBITMAP "installer-side.bmp"
!define MUI_UNFINISHPAGE_NOAUTOCLOSE

;--------------------------------
!include "WordFunc.nsh"
!insertmacro VersionCompare

;--------------------------------
;General

  ;Name and file
  Name "${PROGRAM_NAME} ${PROGRAM_VERSION}"
  OutFile "${PROGRAM_NAME}-${PROGRAM_VERSION}-win32-setup.exe"
  Icon "${icon}"

  SetCompressor lzma
  ;Default installation folder
  InstallDir "$PROGRAMFILES\${PROGRAM_NAME}"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\${PROGRAM_NAME}" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user
  
  # Branding text
  BrandingText "${PROGRAM_NAME} Windows Installer v${AMIR_INSTALLER_VERSION}"

;--------------------------------
;Variables

  Var StartMenuFolder


;Pages

#  !define MUI_WELCOMEPAGE_TITLE "Welcome to Amir setup wizard"
#  !define MUI_WELCOMEPAGE_TEXT "This will install Amir 0.1 on your computer.$\r$\n$\r$\nClick Next to continue, Or Cancel to exit setup."
  !insertmacro MUI_PAGE_WELCOME

  !insertmacro MUI_PAGE_LICENSE "..\COPYING"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Amir" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
  !insertmacro MUI_PAGE_INSTFILES

  #!define MUI_FINISHPAGE_TITLE "Completing Amir setup wizard"
  #!define MUI_FINISHPAGE_TEXT "Congratulations! Setup has finished installing Amir 0.1 on your computer."
  !define MUI_FINISHPAGE_RUN "$INSTDIR\Amir\amir.exe"
  !define MUI_FINISHPAGE_RUN_NOTCHECKED
  !define MUI_FINISHPAGE_RUN_TEXT "Launch Amir"
  !insertmacro MUI_PAGE_FINISH
  
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

# Install main application
Section "Amir accounting software" Section1
  SectionIn RO

  SetOutPath "$INSTDIR"
  File amir.ico
  File license.txt

  CreateDirectory $INSTDIR\Amir
  !cd	build
  SetOutPath "$INSTDIR\Amir"
  File /r *
  !cd ..
  
  ;Store installation folder
  WriteRegStr HKCU "Software\Amir" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ;create desktop shortcut
  CreateShortCut "$DESKTOP\Amir.lnk" "$INSTDIR\Amir\amir.exe" "" "$INSTDIR\${icon}"
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Amir.lnk" "$INSTDIR\Amir\amir.exe" "" "$INSTDIR\${icon}"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  
  !insertmacro MUI_STARTMENU_WRITE_END

  WriteRegStr HKCR "Application\DefaultIcon" "" "$INSTDIR\${icon}"
  ;Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir" "DisplayName" "${PROGRAM_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir" "DisplayVersion" "${PROGRAM_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir" "URLInfoAbout" "http://www.freeamir.com/"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir" "DisplayIcon" "$INSTDIR\${icon}"
  
SectionEnd

;------------------------------------------

# Install GTK+ 2.16
!ifdef GTK_NOTNEEDED
Section /o "GTK+ 2.16 runtime" Section2
!else
Section "GTK+ 2.16 runtime" Section2
!endif

  CreateDirectory $INSTDIR\gtk2
  SetOutPath "$INSTDIR\gtk2"
  File "gtk2-runtime-2.16.6-2010-05-12-ash.exe"
  
  ExecWait '"gtk2-runtime-2.16.6-2010-05-12-ash.exe" /compatdlls=yes /D=$GTK_FOLDER'
  
SectionEnd

Section "Microsoft Visual C++ 2008 Redistributable" Section3

  CreateDirectory $INSTDIR\mvc
  SetOutPath "$INSTDIR\mvc"
  File "vcredist_x86.exe"
  
  ExecWait '"vcredist_x86.exe"'

SectionEnd

LangString DESC_Section1 ${LANG_ENGLISH} "Install Amir accounting software."
LangString DESC_Section2 ${LANG_ENGLISH} "Test"
LangString DESC_Section3 ${LANG_ENGLISH} "Install Microsoft Visual C++ 2008 Redistributable Package. \
  binaries created with python 2.6 or 2.7 will need the Microsoft Visual C++ 2008 Redistributable Package."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
  !insertmacro MUI_DESCRIPTION_TEXT ${Section2} $GTK_INSTALL_HINT
  !insertmacro MUI_DESCRIPTION_TEXT ${Section3} $(DESC_Section3)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;UninstallIcon "${icon}"

  RMDir  /r "$INSTDIR\Amir"
  RMDir  /r "$INSTDIR\gtk2"
  RMDir  /r "$INSTDIR\mvc"
  DELETE "$INSTDIR\amir.ico"
  DELETE "$INSTDIR\license.txt"
  DELETE "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"

  Delete "$DESKTOP\Amir.lnk"
  
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    
  Delete "$SMPROGRAMS\$StartMenuFolder\Amir.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  DeleteRegKey /ifempty HKCU "Software\Amir"
  DeleteRegKey /ifempty HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amir"
  ;DeleteRegKey /ifempty HKCR "Application\DefaultIcon"

SectionEnd

;-------------------------------------
Function .onInit
  ;Check if GTK is installed
  Call DoWeNeedGtk
  Pop $R0
  Pop $R6
  StrCmp $R0 "0" have_gtk
  StrCmp $R0 "1" upgrade_gtk
  StrCmp $R0 "2" upgrade_gtk
  StrCmp $R0 "3" no_gtk no_gtk

  no_gtk:
    ;StrCmp $R1 "NONE" gtk_no_install_rights
    ;ClearErrors
    StrCpy $GTK_INSTALL_HINT "Install the GTK+ 2.16 runtime. \
            You must install the GTK+ 2.16 runtime, or Amir will fail to run on your system."
    Goto done

 upgrade_gtk:
    StrCpy $GTK_FOLDER $R6
    StrCmp $R0 "2" label_needed label_optional ;Upgrade isn't optional
    label_optional:
        StrCpy $GTK_INSTALL_HINT "You have already installed GTK+ runtime in $GTK_FOLDER.  \
            But it's recommended to upgrade it to version 2.16."
    label_needed:
        StrCpy $GTK_INSTALL_HINT "You have already installed GTK+ runtime in $GTK_FOLDER. \
            But should upgrade it to version 2.16."
        Goto done
 
  have_gtk:
    StrCpy $GTK_FOLDER $R6
    !define GTK_NOTNEEDED 1
    StrCpy $GTK_INSTALL_HINT "You have already installed GTK+ runtime 2.16 or above in $GTK_FOLDER \
       There is no need to reinstall it."
    Goto done
 
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end got_install rights
 
  gtk_no_install_rights:
    ; Install GTK+ to Pidgin install dir
    StrCpy $GTK_FOLDER $INSTDIR
    ClearErrors
    Goto done
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end gtk_no_install_rights
 
  done:
    Delete "$TEMP\gtk-runtime.exe"
FunctionEnd

;-------------------------------------
Function .onInstSuccess
  ;Check if GTK is installed
  Call DoWeNeedGtk
  Pop $R0
  Pop $R6 
  StrCmp $R0 "0" gtk_found
  StrCmp $R0 "1" gtk_found
  StrCmp $R0 "2" gtk_found done
  gtk_found:
    StrCpy $GTK_FOLDER $R6
    SetOutPath "$GTK_FOLDER\etc\gtk-2.0"
    SetOverwrite on
    File gtkrc
    SetOverwrite off
  done:

FunctionEnd

;--------------------------------------
;
; Usage:
; Call DoWeNeedGtk
; First Pop:
;   0 - We have the correct version
;       Second Pop: Key where Version was found
;   1 - We have an old version that should work, prompt user for optional upgrade
;       Second Pop: HKLM or HKCU depending on where GTK was found.
;   2 - We have an old version that needs to be upgraded
;       Second Pop: HKLM or HKCU depending on where GTK was found.
;   3 - We don't have Gtk+ at all
;       Second Pop: "NONE, HKLM or HKCU" depending on our rights..
;
Function DoWeNeedGtk
  ; Logic should be:
  ; - Check what user rights we have (HKLM or HKCU)
  ;   - If HKLM rights..
  ;     - Only check HKLM key for GTK+
  ;       - If installed to HKLM, check it and return.
  ;   - If HKCU rights..
  ;     - First check HKCU key for GTK+
  ;       - if good or bad exists stop and ret.
  ;     - If no hkcu gtk+ install, check HKLM
  ;       - If HKLM ver exists but old, return as if no ver exits.
  ;   - If no rights
  ;     - Check HKLM
  Push $0
  Push $1
  Push $2
  Push $3
 
  Call CheckUserInstallRights
  Pop $1
  StrCmp $1 "HKLM" check_hklm
  StrCmp $1 "HKCU" check_hkcu check_hklm
    check_hkcu:
      ReadRegStr $0 HKCU ${GTK_REG_KEY} "Version"
      StrCpy $2 "HKCU"
      StrCmp $0 "" check_hklm have_gtk
 
    check_hklm:
      ReadRegStr $0 HKLM ${GTK_REG_KEY} "Version"
      StrCpy $2 "HKLM"
      StrCmp $0 "" no_gtk have_gtk
 
  have_gtk:
    ; GTK+ is already installed; check version.
    ; Change this to not even run the GTK installer if this version is already installed.
    ${VersionCompare} ${GTK_INSTALL_VERSION} $0 $3
    IntCmp $3 1 +1 good_version good_version
    ${VersionCompare} ${GTK_MIN_VERSION} $0 $3
 
      ; Bad version. If hklm ver and we have hkcu or no rights.. return no gtk
      StrCmp $1 "NONE" no_gtk ; if no rights.. can't upgrade
      StrCmp $1 "HKCU" 0 +2   ; if HKLM can upgrade..
      StrCmp $2 "HKLM" no_gtk ; have hkcu rights.. if found hklm ver can't upgrade..
      Push $2
      IntCmp $3 1 +3
        Push "1" ; Optional Upgrade
        Goto done
        Push "2" ; Mandatory Upgrade
        Goto done
 
  good_version:
    StrCmp $2 "HKLM" have_hklm_gtk have_hkcu_gtk
      have_hkcu_gtk:
        ; Have HKCU version
        ReadRegStr $0 HKCU ${GTK_REG_KEY} "Path"
        Goto good_version_cont
 
      have_hklm_gtk:
        ReadRegStr $0 HKLM ${GTK_REG_KEY} "Path"
        Goto good_version_cont
 
    good_version_cont:
      Push $0  ; The path to existing GTK+
      Push "0"
      Goto done
 
  no_gtk:
    Push $1 ; our rights
    Push "3"
    Goto done
 
  done:
  ; The top two items on the stack are what we want to return
  Exch 4
  Pop $1
  Exch 4
  Pop $0
  Pop $3
  Pop $2
FunctionEnd

!macro CheckUserInstallRightsMacro UN
Function ${UN}CheckUserInstallRights
  Push $0
  Push $1
  ClearErrors
  UserInfo::GetName
  IfErrors Win9x
  Pop $0
  UserInfo::GetAccountType
  Pop $1
 
  StrCmp $1 "Admin" 0 +3
    StrCpy $1 "HKLM"
    Goto done
  StrCmp $1 "Power" 0 +3
    StrCpy $1 "HKLM"
    Goto done
  StrCmp $1 "User" 0 +3
    StrCpy $1 "HKCU"
    Goto done
  StrCmp $1 "Guest" 0 +3
    StrCpy $1 "NONE"
    Goto done
  ; Unknown error
  StrCpy $1 "NONE"
  Goto done
 
  Win9x:
    StrCpy $1 "HKLM"
 
  done:
    Exch $1
    Exch
    Pop $0
FunctionEnd
!macroend
!insertmacro CheckUserInstallRightsMacro ""
;!insertmacro CheckUserInstallRightsMacro "un."
 
