;--------------------------------
;Global Variables



;--------------------------------
;Defines

!define icon "amir.ico"
!define PROGRAM_NAME "Amir"
!define PROGRAM_VERSION "0.2.0"
!define PROGRAM_WEB_SITE "http://www.freeamir.com"
!define AMIR_INSTALLER_VERSION "0.2.0"

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
  ; RequestExecutionLevel admin
  ;Name and file
  Name "${PROGRAM_NAME} ${PROGRAM_VERSION}"
  OutFile "${PROGRAM_NAME}-${PROGRAM_VERSION}-win64-setup.exe"
  Icon "${icon}"

  SetCompressor lzma
  ;Default installation folder
  InstallDir "$PROGRAMFILES64\${PROGRAM_NAME}"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\${PROGRAM_NAME}" ""

  ;Request application privileges for Windows Vista
  ;RequestExecutionLevel admin

  # Branding text
  BrandingText "${PROGRAM_NAME} Windows Installer v${AMIR_INSTALLER_VERSION}"

;--------------------------------
;Variables

  Var StartMenuFolder


;Pages

#  !define MUI_WELCOMEPAGE_TITLE "Welcome to Amir setup wizard"
#  !define MUI_WELCOMEPAGE_TEXT "This will install Amir 0.2.0 on your computer.$\r$\n$\r$\nClick Next to continue, Or Cancel to exit setup."
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

  !define MUI_FINISHPAGE_TITLE "Completing Amir setup wizard"
  !define MUI_FINISHPAGE_TEXT "Congratulations! Setup has finished installing Amir 0.2.0 on your computer."
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
  !cd	dist/amir
  SetOutPath "$INSTDIR\Amir"
  File /r *
  !cd ../../

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


LangString DESC_Section1 ${LANG_ENGLISH} "Install Amir accounting software."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;UninstallIcon "${icon}"

  RMDir  /r "$INSTDIR\Amir"
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
