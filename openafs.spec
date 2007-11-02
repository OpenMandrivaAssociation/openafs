%define name    openafs
%define version 1.4.5
%define release %mkrel 1
%define dkms_version %{version}-%{release}
%define module  libafs
%define major   1
%define libname %mklibname %{name} %{major}
%define _requires_exceptions libafsrpc.so

Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        OpenAFS distributed filesystem
Group:          Networking/Other
License:        IBM
URL:            http://openafs.org/
Source0:        http://www.openafs.org/dl/openafs/%{version}/openafs-%{version}-src.tar.bz2
Source1:        http://www.openafs.org/dl/openafs/%{version}/openafs-%{version}-doc.tar.bz2
Source2:        http://grand.central.org/dl/cellservdb/CellServDB
Source3:        openafs.init
Source4:        openafs.config
Source5:        openafs-server.init
BuildRequires:  pam-devel
BuildRequires:  ncurses-devel
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  krb5-devel
Requires:       kmod(libafs)
Conflicts:      krbafs-utils
Conflicts:      coda-debug-backup
BuildRoot:      %{_tmppath}/%{name}-%{version}

%description
AFS is a distributed filesystem allowing cross-platform sharing of files
among multiple computers. Facilities are provided for access control,
authentication, backup and administrative management.

This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.

%package client
Summary:        OpenAFS filesystem client
Group:          Networking/Other
Requires:       %{name} = %{version}
Requires(post,preun): rpm-helper

%description client
AFS is a distributed filesystem allowing cross-platform sharing of files
among multiple computers. Facilities are provided for access control,
authentication, backup and administrative management.

This package provides basic client support to mount and manipulate
AFS.

%package server
Summary:        OpenAFS filesystem server
Group:          Networking/Other
Requires:       %{name}-client = %{version}

%description server
AFS is a distributed filesystem allowing cross-platform sharing of files
among multiple computers. Facilities are provided for access control,
authentication, backup and administrative management.

This package provides basic server support to host files in an AFS
cell.

%package -n %{libname}
Summary:        Libraries for %{name}
Group:          System/Libraries

%description -n	%{libname}
This package contains the libraries needed to run programs dynamically
linked with OpenAFS libraries.

%package -n %{libname}-devel
Summary:        Static libraries and header files for OpenAFS
Group:          Development/C
Provides:       %{name}-devel = %{version}-%{release}
Provides:       lib%{name}-devel = %{version}-%{release}
Requires:       %{libname} = %{version}
Conflicts:      %mklibname -d lwp 2
Conflicts:      %mklibname -d rplay

%description -n	%{libname}-devel
This package contains the static development libraries and headers needed
to compile applications linked with OpenAFS libraries.

%package -n dkms-%{module}
Summary:        DKMS-ready kernel source for AFS distributed filesystem
Group:          Development/Kernel
Obsoletes:      openafs-kernel-source
Provides:       openafs-kernel-source
Requires(pre):  dkms
Requires(pre):  flex
Requires(post): dkms
Provides:       kmod(libafs)

%description -n dkms-%{module}
This package provides the AFS kernel module.

%package doc
Summary:        OpenAFS doc
Group:          Networking/Other
Conflicts:      up

%description doc
This packages provides the documentation for OpenAFS.


%prep
%setup -q -T -b 0
%setup -q -T -D -b 1
chmod 644 doc/html/QuickStartWindows/*.htm

%build
%serverbuild
%ifarch x86_64
%define sysname amd64_linux26
%else
%define sysname %{_arch}_linux26
%endif

%configure \
	--disable-kernel-module \
	--with-afs-sysname=%{sysname} \
	--with-krb5-conf=%{_bindir}/krb5-config

make all_nolibafs
make libafs_tree

%install
rm -rf %{buildroot}
make install_nolibafs DESTDIR=%{buildroot}

# cache
install -m 755 -d %{buildroot}/var/cache/%{name}

# configuration
install -m 755 -d %{buildroot}%{_sysconfdir}/%{name}
install -m 644 %{SOURCE2}  %{buildroot}%{_sysconfdir}/%{name}/CellServDB

# init script
install -m 755 -d %{buildroot}%{_initrddir}
install -m 755 -d %{buildroot}%{_sysconfdir}/sysconfig
install -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/%{name}
install -m 755 %{SOURCE5} %{buildroot}%{_initrddir}/%{name}-server
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# kernel module
install -d -m 755 %{buildroot}%{_prefix}/src
cp -a libafs_tree %{buildroot}%{_prefix}/src/%{module}-%{dkms_version}

cat > %{buildroot}%{_prefix}/src/%{module}-%{dkms_version}/dkms.conf <<EOF

PACKAGE_VERSION="%{dkms_version}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{module}"
MAKE[0]="SMP=SP; eval \\\`grep CONFIG_SMP /boot/config-\${kernelver_array[0]}\\\`; [ -n \"\\\$CONFIG_SMP\" ] && SMP=MP; ./configure --with-linux-kernel-headers=\${kernel_source_dir}; make MPS=\\\$SMP; mv src/libafs/MODLOAD-*/libafs.ko ."
CLEAN="make -C src/libafs clean"

BUILT_MODULE_NAME[0]="\$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/kernel/3rdparty/\$PACKAGE_NAME/"

AUTOINSTALL=yes

EOF

# clean up stuff that we don't want to package

# DCE security system stuff -- wasn't included before -- is this
# of use to anyone?
rm %{buildroot}%{_bindir}/dlog
rm %{buildroot}%{_bindir}/dpass

# this is coming out 0 bytes. And it wasn't getting packaged before.
rm %{buildroot}%{_sbindir}/kdump

# we don't use these.... Red Hat has its own pam_krb5afs modules.
# maybe in the future, we could configure these instead....
#rm %{buildroot}%{_libdir}/pam_afs.krb.so.1
#rm %{buildroot}%{_libdir}/pam_afs.so.1

# e2fsprogs-devel has one of these.
rm %{buildroot}%{_bindir}/compile_et

%multiarch_binaries %{buildroot}%{_bindir}/rxgen
%multiarch_binaries %{buildroot}%{_bindir}/xstat_cm_test
%multiarch_binaries %{buildroot}%{_bindir}/xstat_fs_test
%multiarch_includes %{buildroot}%{_includedir}/afs/dirpath.h
%multiarch_includes %{buildroot}%{_includedir}/afs/param.h

# rename binaries and man page to avoid some conflicts
mv %{buildroot}%{_bindir}/kpasswd{,.afs}
mv %{buildroot}%{_bindir}/up{,.afs}
mv %{buildroot}%{_mandir}/man1/kpasswd.1 \
    %{buildroot}%{_mandir}/man1/kpasswd.afs.1
mv %{buildroot}%{_mandir}/man1/up.1 \
    %{buildroot}%{_mandir}/man1/up.afs.1
mv %{buildroot}%{_mandir}/man8/upclient.8 \
    %{buildroot}%{_mandir}/man8/upclient.afs.8

# fix generated files
perl -pi -e 's|%{_builddir}/%{name}-%{version}/src|../..|' \
    %{buildroot}%{_prefix}/src/libafs-%{version}-%{release}/src/config/Makefile.version

%clean
rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post client
%_post_service %{name}
if [ ! -e /mnt/afs ]; then
	mkdir /mnt/afs
fi

%preun client
%_preun_service %{name}

%post -n dkms-%{module}
dkms add -m %{module} -v %{dkms_version} --rpm_safe_upgrade
dkms build -m %{module} -v %{dkms_version} --rpm_safe_upgrade
dkms install -m %{module} -v %{dkms_version} --rpm_safe_upgrade

%preun -n dkms-%{module}
dkms remove -m %{module} -v %{dkms_version} --rpm_safe_upgrade --all ||:

%files
%defattr(-,root,root,-)
%doc README NEWS src/LICENSE
%{_bindir}/asetkey
%{_bindir}/afsmonitor
%{_bindir}/bos
%{_bindir}/fs
%{_bindir}/kpasswd.afs
%{_bindir}/kpwvalid
%{_bindir}/klog
%{_bindir}/klog.krb
%{_bindir}/aklog
%{_bindir}/knfs
%{_bindir}/livesys
%{_bindir}/pagsh
%{_bindir}/pagsh.krb
%{_bindir}/pts
%{_bindir}/scout
%{_bindir}/sys
%{_bindir}/tokens
%{_bindir}/tokens.krb
%{_bindir}/translate_et
%{_bindir}/udebug
%{_bindir}/unlog
%{_sbindir}/backup
%{_sbindir}/bos_util
%{_sbindir}/butc
%{_sbindir}/copyauth
%{_sbindir}/fms
%{_sbindir}/fstrace
%{_sbindir}/kas
%{_sbindir}/read_tape
%{_sbindir}/restorevol
%{_sbindir}/rxdebug
%{_sbindir}/uss
%{_sbindir}/vos
%{_mandir}/man1/afsmonitor.1*
%{_mandir}/man1/fs.1*
%{_mandir}/man1/klog.1*
%{_mandir}/man1/knfs.1*
%{_mandir}/man1/livesys.1*
%{_mandir}/man1/pagsh.1*
%{_mandir}/man1/pts.1*
%{_mandir}/man1/scout.1*
%{_mandir}/man1/sys.1*
%{_mandir}/man1/tokens.1*
%{_mandir}/man1/translate_et.1*
%{_mandir}/man1/udebug.1*
%{_mandir}/man1/unlog.1*
%{_mandir}/man1/rxdebug.1*
%{_mandir}/man1/vos.1*
%{_mandir}/man1/kpasswd.afs.1*

%files client
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_initrddir}/%{name}
%{_bindir}/cmdebug
%{_bindir}/up.afs
%{_sbindir}/afsd
%{_mandir}/man1/up.afs.1*
/var/cache/%{name}

%files server
%defattr(-,root,root)
%{_initrddir}/%{name}-server
%{_sbindir}/bosserver
%{_sbindir}/ka-forwarder
%{_sbindir}/kadb_check
%{_sbindir}/kdb
%{_sbindir}/kpwvalid
%{_sbindir}/prdb_check
%{_sbindir}/pt_util
%{_sbindir}/rmtsysd
%{_sbindir}/vldb_check
%{_sbindir}/vldb_convert
%{_sbindir}/voldump
%{_sbindir}/volinfo
%{_sbindir}/vsys
%{_libdir}/openafs
%{_mandir}/man8/bosserver.8*
%{_mandir}/man8/kadb_check.8*
%{_mandir}/man8/kdb.8*
%{_mandir}/man8/kpwvalid.8*
%{_mandir}/man8/prdb_check.8*
%{_mandir}/man8/vldb_check.8*
%{_mandir}/man8/voldump.8*
%{_mandir}/man8/volinfo.8*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%multiarch %{multiarch_bindir}/rxgen
%multiarch %{multiarch_bindir}/xstat_cm_test
%multiarch %{multiarch_bindir}/xstat_fs_test
%{_bindir}/rxgen
%{_bindir}/xstat_cm_test
%{_bindir}/xstat_fs_test
%{_includedir}/*.h
%{_includedir}/afs
%{_includedir}/rx
%multiarch %{multiarch_includedir}/afs
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/afs

%files -n dkms-%{module}
%defattr(-,root,root)
%{_prefix}/src/%{module}-%{dkms_version}

%files doc
%defattr(-,root,root)
%doc doc/LICENSE doc/pdf doc/txt doc/examples
%{_mandir}/man?/*
%exclude %{_mandir}/man1/afsmonitor.1*
%exclude %{_mandir}/man1/fs.1*
%exclude %{_mandir}/man1/klog.1*
%exclude %{_mandir}/man1/knfs.1*
%exclude %{_mandir}/man1/livesys.1*
%exclude %{_mandir}/man1/pagsh.1*
%exclude %{_mandir}/man1/pts.1*
%exclude %{_mandir}/man1/scout.1*
%exclude %{_mandir}/man1/sys.1*
%exclude %{_mandir}/man1/tokens.1*
%exclude %{_mandir}/man1/translate_et.1*
%exclude %{_mandir}/man1/udebug.1*
%exclude %{_mandir}/man1/unlog.1*
%exclude %{_mandir}/man1/rxdebug.1*
%exclude %{_mandir}/man1/vos.1*
%exclude %{_mandir}/man1/up.afs.1*
%exclude %{_mandir}/man1/kpasswd.afs.1*
%exclude %{_mandir}/man8/bosserver.8*
%exclude %{_mandir}/man8/kadb_check.8*
%exclude %{_mandir}/man8/kdb.8*
%exclude %{_mandir}/man8/kpwvalid.8*
%exclude %{_mandir}/man8/prdb_check.8*
%exclude %{_mandir}/man8/vldb_check.8*
%exclude %{_mandir}/man8/voldump.8*
%exclude %{_mandir}/man8/volinfo.8*


