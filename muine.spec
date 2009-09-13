%define version 0.8.11
%define pre 0
%if %pre
%define fname %name-%version%pre
%else
%define fname %name-%version
%endif
%define release %mkrel 1

%define req_mono_version 0.91
%define gtk_sharp_version 1.9.2

%define	gstname gstreamer0.10
%define gstver 0.10.0

%define monoprefix %_prefix/lib
Summary:	Music player for GNOME
Name:		muine
Version:	%{version}
Release:	%{release}
License:	GPLv2+
Group:		Sound
URL:		http://muine-player.org/
Buildroot:	%{_tmppath}/%{name}-%{version}-buildroot
Source:		http://ftp.gnome.org/pub/GNOME/sources/%name/%fname.tar.bz2
#gw hardcode plugins dir so plugin packages can be noarch
Patch: 		muine-0.8.3-plugindir.patch
BuildRequires:	gdbm-devel
BuildRequires:	gnome-sharp2-devel >= %gtk_sharp_version
BuildRequires:	mono-tools
BuildRequires:	gtk+2-devel
BuildRequires:	libGConf2-devel
BuildRequires:	mono-devel >= %{req_mono_version}
BuildRequires:  ndesk-dbus-glib
BuildRequires:	taglib-sharp
# gw for the automatic mono deps
BuildRequires:	libmusicbrainz-devel libnotify-devel
BuildRequires:	imagemagick
BuildRequires:	intltool
#BuildRequires:	gnome-common 
Requires:	mono >= %{req_mono_version}
Requires: shared-mime-info >= 0.16
BuildRequires:	libgstreamer-plugins-base-devel >= %gstver
Requires:	%gstname-plugins-good
Requires:	%gstname-plugins-base
Requires:	%gstname-plugins-bad >= %gstver
Requires:	%gstname-flac >= %gstver
Suggests: %gstname-faad >= %gstver
BuildRequires: desktop-file-utils
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description
Muine is a music player for GNOME. Its UI has been designed from the
ground up to be very comfortable, and not just a clone of iTunes.
It is playlist-based, but does have a music library (not a traditional
one, though).

%package trayicon
Summary: TrayIcon plugin for muine
Group: Sound
Requires: %{_lib}notify1
Requires: %name = %version

%description trayicon
This is a tray icon for the muine music player.

%package doc
Summary: Development documentation for %name
Group: Development/Other
Requires(post): mono-tools >= 1.1.9
Requires(postun): mono-tools >= 1.1.9

%description doc
This package contains the API documentation for the %name in
Monodoc format.

%prep
%setup -q -n %fname
%patch -p1

%build
%define _disable_ld_no_undefined 1
# lower optimization, seems to be more stable
CFLAGS=`echo %{optflags} | sed 's/-O[0-9]/-O/'`
%configure2_5x


make LIBS=-lX11

%install
rm -rf %{buildroot}
GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1 %makeinstall_std
rm -rf %buildroot%_libdir/muine/plugins

#gw installed to the wrong dir
mkdir -p %buildroot%monoprefix/monodoc/sources/
mv %buildroot%_datadir/doc/muine/muine-docs* %buildroot%monoprefix/monodoc/sources/

%find_lang %name
# menu entry

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="Audio;Player" \
  --add-category="X-Mandriva-Multimedia-Sound" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*


# icons
mkdir -p %{buildroot}%{_liconsdir} %{buildroot}%{_miconsdir}
convert -scale 48x48   ./data/images/muine-scalable.svg %{buildroot}%{_liconsdir}/muine.png
install -m 644 ./data/images/muine-32.png %{buildroot}%{_iconsdir}/muine.png
install -m 644 ./data/images/muine-16.png %{buildroot}%{_miconsdir}/muine.png

# remove unwanted files
rm -f %{buildroot}%{_libdir}/%{name}/lib*.{a,la}
rm -f %{buildroot}%{_libdir}/%{name}/NDesk.DBus*

#add the plugins
mkdir -p %buildroot%monoprefix/%name/plugins
install -m 644 plugins/*.dll plugins/*.dll.config %buildroot%monoprefix/%name/plugins/

%if %mdkversion < 200900
%post
%update_menus
%update_desktop_database
%post_install_gconf_schemas muine
%update_icon_cache hicolor
%endif

%preun
%preun_uninstall_gconf_schemas muine

%if %mdkversion < 200900
%postun
%clean_menus
%clean_desktop_database
%clean_icon_cache hicolor
%endif

%post doc
%_bindir/monodoc --make-index > /dev/null

%postun doc
if [ "$1" = "0" -a -x %_bindir/monodoc ]; then %_bindir/monodoc --make-index > /dev/null
fi



%clean
rm -rf %{buildroot}

%files -f %name.lang
%defattr(-, root, root)
%doc AUTHORS ChangeLog NEWS README TODO
%{_sysconfdir}/gconf/schemas/*.schemas
%{_bindir}/*
%dir %monoprefix/%{name}
%dir %monoprefix/%{name}/plugins
%monoprefix/%{name}/plugins/InotifyPlugin.dll
%monoprefix/%{name}/plugins/InotifyPlugin.dll.config
%dir %_libdir/%name
%_libdir/%name/*muine*
%_libdir/%name/libinotifyglue.so*
%_datadir/dbus-1/services/org.gnome.Muine.service
%_libdir/pkgconfig/*.pc
%{_datadir}/applications/*.desktop
%_datadir/icons/hicolor/*/*/muine*
%{_iconsdir}/muine.png
%{_miconsdir}/muine.png
%{_liconsdir}/muine.png

%files trayicon
%defattr(-,root,root)
%monoprefix/%{name}/plugins/TrayIcon.dll
%monoprefix/%{name}/plugins/TrayIcon.dll.config

%files doc
%defattr(-,root,root)
%monoprefix/monodoc/sources/*


