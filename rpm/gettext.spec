# specfile originally created for Fedora, modified for MeeGo Linux

# The split of gettext into two packages is suggested by upstream (see
# the PACKAGING file). Here we name gettext-runtime as
# gettext-lib. Please be noted that gettext-runtime is LGPL while the
# others parts are of GPL. You should be careful of the license when
# adding files into these sub-packages.

# libintl.jar requires gcj >= 4.3 to build
%define enable_testing 0

Name:           gettext
Version:        0.19.8.1
Release:        1
License:        GPLv3+ and LGPLv2+
Summary:        GNU libraries and utilities for producing multi-lingual messages
Url:            http://www.gnu.org/software/gettext/
Group:          Development/Tools
Source:         ftp://ftp.gnu.org/gnu/gettext/%{name}-%{version}.tar.gz
Source2:        msghack.py
Patch0:         0001-Remove-html-docs.patch

# Bootstrapping
BuildRequires:  autoconf >= 2.5
BuildRequires:  bison >= 3.0
BuildRequires:  libtool

BuildRequires:  gcc-c++

# Needed to gettext-tools/gnulib-lib/Makefile etc.
BuildRequires:  gperf

# makeinfo is required for build
BuildRequires:  texinfo

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

Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

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
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-libs = %{version}-%{release}
Requires:       xz
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

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
Group:          System/Libraries

%description libs
This package contains libraries used internationalization support.

%prep
%setup -q -n %{name}-%{version}/%{name}
%patch0 -p1

%build
echo %{version} | cut -d '+' -f 1 > .tarball-version
cp .tarball-version .version
cp ../archive.dir.tar.xz gettext-tools/misc

GNULIB_SRCDIR=../gnulib/ ./autogen.sh --no-git
[ -f %{_datadir}/automake/depcomp ] && cp -f %{_datadir}/automake/{depcomp,ylwrap} .

%ifarch %arm aarch64
# We add a compile flag for ARM to deal with a bug in qemu (msgmerge using pthread/gomp)
# msgmerge will lockup during execution.
%define addconfflag --without-libpth-prefix --disable-openmp
%endif

%configure --without-included-gettext \
    --enable-nls \
    --disable-static \
    --enable-shared \
    --with-pic-=yes \
    --with-included-glib \
    --with-included-libxml \
    --disable-curses \
    --disable-csharp %addconfflag

# TODO: %{?jobs:-j%jobs} is removed here as the build fails to following error with it.
# make[4]: *** No rule to make target `cldr-plural.h', needed by `all'.  Stop.
make GCJFLAGS="-findirect-dispatch"

%install
make install DESTDIR=%{buildroot} INSTALL="%{__install} -p" \
    lispdir=%{_datadir}/emacs/site-lisp \
    aclocaldir=%{_datadir}/aclocal EXAMPLESFILES=""

# move gettext to /bin
mkdir -p %{buildroot}/bin
mv %{buildroot}%{_bindir}/gettext %{buildroot}/bin
ln -s ../../bin/gettext %{buildroot}%{_bindir}/gettext

install -pm 755 %SOURCE2 %{buildroot}%{_bindir}/msghack

# make preloadable_libintl.so executable
chmod 755 %{buildroot}%{_libdir}/preloadable_libintl.so

rm -f %{buildroot}%{_infodir}/dir

# doc relocations
for i in gettext-runtime/man/*.html; do
  rm %{buildroot}%{_datadir}/doc/gettext/`basename $i`
done
rm -r %{buildroot}%{_datadir}/doc/gettext/javadoc*

rm -rf %{buildroot}%{_datadir}/doc/gettext/examples

rm -rf htmldoc
mkdir htmldoc
mv %{buildroot}%{_datadir}/doc/gettext/* %{buildroot}%{_datadir}/doc/libasprintf/* htmldoc
rm -r %{buildroot}%{_datadir}/doc/libasprintf
rm -r %{buildroot}%{_datadir}/doc/gettext

# own this directory for third-party *.its files
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/its

# remove unpackaged files from the buildroot
rm -rf %{buildroot}%{_datadir}/emacs
rm %{buildroot}%{_libdir}/lib*.la

%find_lang %{name}-runtime
%find_lang %{name}-tools
cat %{name}-*.lang > %{name}.lang

%check
%if %{enable_testing}
make check
%endif

%define install_info /sbin/install-info
%define remove_install_info /sbin/install-info --delete

%post
/sbin/ldconfig
[ -e %{_infodir}/gettext.info.gz ] && %{install_info} %{_infodir}/gettext.info.gz %{_infodir}/dir || :

%preun
if [ "$1" = 0 ]; then
    [ -e %{_infodir}/gettext.info.gz ] && %{remove_install_info} %{_infodir}/gettext.info.gz %{_infodir}/dir || :
fi
exit 0

%postun -p /sbin/ldconfig

%post devel
/sbin/ldconfig
[ -e %{_infodir}/autosprintf.info ] && %{install_info} %{_infodir}/autosprintf.info %{_infodir}/dir || :

%preun devel
/sbin/ldconfig
if [ "$1" = 0 ]; then
    [ -e %{_infodir}/autosprintf.info ] && %{remove_install_info} %{_infodir}/autosprintf.info %{_infodir}/dir || :
fi

%postun devel -p /sbin/ldconfig

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
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
%doc %{_infodir}/autosprintf*
%doc %{_infodir}/gettext*
%doc gettext-runtime/intl-java/javadoc*
%doc %{_mandir}/man1/autopoint.1.gz
%doc %{_mandir}/man1/gettextize.1.gz
%doc %{_mandir}/man1/msgattrib.1.gz
%doc %{_mandir}/man1/msgcat.1.gz
%doc %{_mandir}/man1/msgcmp.1.gz
%doc %{_mandir}/man1/msgcomm.1.gz
%doc %{_mandir}/man1/msgconv.1.gz
%doc %{_mandir}/man1/msgen.1.gz
%doc %{_mandir}/man1/msgexec.1.gz
%doc %{_mandir}/man1/msgfilter.1.gz
%doc %{_mandir}/man1/msgfmt.1.gz
%doc %{_mandir}/man1/msggrep.1.gz
%doc %{_mandir}/man1/msginit.1.gz
%doc %{_mandir}/man1/msgmerge.1.gz
%doc %{_mandir}/man1/msgunfmt.1.gz
%doc %{_mandir}/man1/msguniq.1.gz
%doc %{_mandir}/man1/recode-sr-latin.1.gz
%doc %{_mandir}/man1/xgettext.1.gz
%{_datadir}/%{name}/projects/
%{_datadir}/%{name}/config.rpath
%{_datadir}/%{name}/*.h
%{_datadir}/%{name}/intl
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
/bin/gettext
%{_bindir}/gettext
%{_bindir}/ngettext
%{_bindir}/envsubst
%{_bindir}/gettext.sh
%doc %{_mandir}/man1/gettext.1.gz
%doc %{_mandir}/man1/ngettext.1.gz
%doc %{_mandir}/man1/envsubst.1.gz
%doc %{_mandir}/man3/*
%{_libdir}/libasprintf.so.*
