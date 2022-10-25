# specfile originally created for Fedora, modified for MeeGo Linux

# The split of gettext into two packages is suggested by upstream (see
# the PACKAGING file). Here we name gettext-runtime as
# gettext-lib. Please be noted that gettext-runtime is LGPL while the
# others parts are of GPL. You should be careful of the license when
# adding files into these sub-packages.

# libintl.jar requires gcj >= 4.3 to build
%define enable_testing 0

Name:           gettext
Version:        0.21.1
Release:        1
License:        GPLv3+ and LGPLv2+ and GFDL
Summary:        GNU libraries and utilities for producing multi-lingual messages
Url:            http://www.gnu.org/software/gettext/
Source:         %{name}-%{version}.tar.gz
Source2:        msghack.py
Patch1:         0001-Export-GNULIB_TOOL-for-libtextstyle-autogen.sh.patch
Patch2:         0002-Disable-man-and-doc-from-gettext-runtime.patch
Patch3:         0003-Disable-man-doc-and-examples-from-gettext-tools.patch
Patch4:         0004-Disable-doc-from-libtextstyle.patch
Patch5:         0005-Disable-man-and-doc-from-libasprintf.patch

# Bootstrapping
BuildRequires:  autoconf >= 2.62
BuildRequires:  automake
BuildRequires:  bison >= 3.0
BuildRequires:  libtool
BuildRequires:  xz

BuildRequires:  gcc-c++

# Needed to gettext-tools/gnulib-lib/Makefile etc.
BuildRequires:  gperf

# need expat for xgettext on glade
BuildRequires:  pkgconfig(expat)

# Requiring pkgconfig(libxml-2.0) or pkgconfig(glib-2.0) here as buildrequires
# is not really an option as that introduces more loops to builds. Thus use the 
# versions that are bundled in.
# E.g. glib2 build fails if gettext has dependency to glib2.

# gettext is required to build tools when we are not cross compiling,
# see gettext/gettext-tools/po/Makefile.in.in for more info.
BuildRequires: gettext-devel

Requires:       %{name}-devel = %{version}

%description
The GNU gettext package provides a set of tools and documentation for
producing multi-lingual messages in programs. Tools include a set of
conventions about how programs should be written to support message
catalogs, a directory and file naming organization for the message
catalogs, a runtime library which supports the retrieval of translated
messages, and stand-alone programs for handling the translatable and
the already translated strings. Gettext provides an easy to use
library and tools for creating, using, and modifying natural language
catalogs and is a powerful and simple method for internationalizing
programs.

MeeGo's gettext is split into two packages: gettext-libs and
gettext-devel. gettext-libs is an LGPLv2+ package that contains
libraries and runtime needed by i18n programs; gettext-devel is used
only for development and building -- and shouldn't be needed by end
users.  This gettext package is a meta-package that depends on
gettext-devel for transition.

%package devel
# autopoint is GPLv3+
# libasprintf is LGPLv2+
# libgettextpo is GPLv3+
License:        LGPLv2+ and GPLv3+
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-libs = %{version}-%{release}
Requires:       libtextstyle = %{version}-%{release}
Requires:       xz
Requires:       diffutils

%description devel
This package contains all development related files necessary for
developing or compiling applications/libraries that needs
internationalization capability. You also need this package if you
want to add gettext support for your project.

%package libs
# libasprintf is LGPLv2+
# libgettextpo is GPLv3+
License:        LGPLv2+ and GPLv3+
Summary:        Libraries for %{name}

%description libs
This package contains libraries used internationalization support.

%package -n libtextstyle
Summary: Text styling library
License: GPLv3+

%description -n libtextstyle
Library for producing styled text to be displayed in a terminal
emulator.

%package -n libtextstyle-devel
Summary: Development files for libtextstyle
License: GPLv3+ and GFDL
Requires: libtextstyle%{?_isa} = %{version}-%{release}

%description -n libtextstyle-devel
This package contains all development related files necessary for
developing or compiling applications/libraries that needs text
styling.

%prep
%autosetup -p1 -n %{name}-%{version}/%{name}

%build
echo %{version} | cut -d '+' -f 1 > .tarball-version
cp .tarball-version .version
cp ../archive.dir.tar.xz gettext-tools/misc
mkdir -p libtextstyle/build-aux
cp ../gnulib/build-aux/texinfo.tex libtextstyle/build-aux/

GNULIB_SRCDIR=$(pwd)/../gnulib/ ./autogen.sh
[ -f %{_datadir}/automake/depcomp ] && cp -f %{_datadir}/automake/{depcomp,ylwrap} .

%configure \
    --enable-nls \
    --disable-static \
    --enable-shared \
    --with-pic-=yes \
    --with-included-glib \
    --with-included-libxml \
    --disable-curses \
    --disable-csharp \
    --disable-rpath \
    --disable-java \
    --disable-native-java

%make_build

%install
%make_install \
    lispdir=%{_datadir}/emacs/site-lisp/gettext \
    aclocaldir=%{_datadir}/aclocal EXAMPLESFILES=""

install -pm 755 %SOURCE2 %{buildroot}%{_bindir}/msghack

# make preloadable_libintl.so executable
chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/preloadable_libintl.so

rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir

rm -rf htmldoc
mkdir htmldoc
mv ${RPM_BUILD_ROOT}%{_datadir}/doc/gettext/* htmldoc
rm -r ${RPM_BUILD_ROOT}%{_datadir}/doc/gettext

# own this directory for third-party *.its files
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}/its

# remove internal .so lib files
rm ${RPM_BUILD_ROOT}%{_libdir}/libgettext{src,lib}.so

%find_lang %{name}-runtime
%find_lang %{name}-tools
cat %{name}-*.lang > %{name}.lang

%check
%if %{enable_testing}
make check
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel -p /sbin/ldconfig

%postun devel -p /sbin/ldconfig

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post -n libtextstyle -p /sbin/ldconfig

%postun -n libtextstyle -p /sbin/ldconfig

%post -n libtextstyle-devel -p /sbin/ldconfig

%postun -n libtextstyle-devel -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license COPYING
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/its
%{_datadir}/%{name}-*/its
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/cldr-plurals

%files devel -f %{name}.lang
%defattr(-,root,root,-)
%doc NEWS THANKS
%doc COPYING gettext-tools/misc/DISCLAIM README
%doc ChangeLog
%{_datadir}/%{name}/projects/
%{_datadir}/%{name}/config.rpath
%{_datadir}/%{name}/*.h
%{_datadir}/%{name}/po
%{_datadir}/%{name}/msgunfmt.tcl
%{_datadir}/aclocal/*
%{_includedir}/*
%{_libdir}/libasprintf.so
%{_libdir}/libgettextpo.so
%{_libdir}/libgettextlib*.so
%{_libdir}/libgettextsrc*.so
%{_libdir}/preloadable_libintl.so
%{_libdir}/gettext/hostname
%{_libdir}/gettext/project-id
%{_libdir}/gettext/urlget
%{_libdir}/gettext/user-email
%{_libdir}/libgettextpo.so.*
%{_datadir}/%{name}/javaversion.class
%{_datadir}/%{name}/archive*.tar.*
%{_datadir}/%{name}/styles
%{_bindir}/autopoint
%{_bindir}/gettextize
%{_bindir}/msgattrib
%{_bindir}/msgcat
%{_bindir}/msgcmp
%{_bindir}/msgcomm
%{_bindir}/msgconv
%{_bindir}/msgen
%{_bindir}/msgexec
%{_bindir}/msgfilter
%{_bindir}/msgfmt
%{_bindir}/msggrep
%{_bindir}/msghack
%{_bindir}/msginit
%{_bindir}/msgmerge
%{_bindir}/msgunfmt
%{_bindir}/msguniq
%{_bindir}/recode-sr-latin
%{_bindir}/xgettext
   
# Don't include language files here since that may inadvertently
# involve unneeded files. If you need to include a file in -libs, list
# it here explicitly
%files libs
%defattr(-,root,root,-)
# Files listed here should be of LGPL license only, refer to upstream
# statement in PACKAGING file
%doc AUTHORS gettext-runtime/BUGS
%doc gettext-runtime/intl/COPYING*
%doc %{_datadir}/gettext/ABOUT-NLS
%{_bindir}/gettext
%{_bindir}/ngettext
%{_bindir}/envsubst
%{_bindir}/gettext.sh
%{_libdir}/libasprintf.so.*

%files -n libtextstyle
%{_libdir}/libtextstyle.so.0*

%files -n libtextstyle-devel
%license libtextstyle/COPYING
%{_includedir}/textstyle/
%{_includedir}/textstyle.h
%{_libdir}/libtextstyle.so
