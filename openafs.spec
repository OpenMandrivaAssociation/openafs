%define name    openafs
%define version 1.4.14
%define release %mkrel 2
%define dkms_version %{version}-%{release}
%define module  libafs
%define major   1
%define libname     %mklibname %{name} %{major}
%define develname	%mklibname %{name} -d
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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
linked with %{name}.

%package -n %{develname}
Summary:    Static libraries and header files for %{name}
Group:      Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:  %mklibname -d %name 1
Conflicts:  %mklibname -d lwp 2
Conflicts:  %mklibname -d rplay

%description -n	%{develname}
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

#aclocal -I src/cf
#autoconf
#autoconf configure-libafs.in > configure-libafs
#chmod +x configure-libafs
#autoheader

%build
%serverbuild
%ifarch x86_64
%define sysname amd64_linux26
%else
%define sysname %{_arch}_linux26
%endif

%configure2_5x \
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

%multiarch_binaries %{buildroot}%{_bindir}/rxgen

%multiarch_binaries %{buildroot}%{_bindir}/xstat_cm_test

%multiarch_binaries %{buildroot}%{_bindir}/xstat_fs_test

%multiarch_includes %{buildroot}%{_includedir}/afs/dirpath.h

%multiarch_includes %{buildroot}%{_includedir}/afs/param.h

# rename binaries and man page to avoid some conflicts
mv %{buildroot}%{_bindir}/kpasswd{,.afs}
mv %{buildroot}%{_bindir}/pagsh{,.afs}
mv %{buildroot}%{_bindir}/up{,.afs}
mv %{buildroot}%{_mandir}/man1/kpasswd.1 \
    %{buildroot}%{_mandir}/man1/kpasswd.afs.1
mv %{buildroot}%{_mandir}/man1/pagsh.1 \
    %{buildroot}%{_mandir}/man1/pagsh.afs.1
mv %{buildroot}%{_mandir}/man1/up.1 \
    %{buildroot}%{_mandir}/man1/up.afs.1
mv %{buildroot}%{_mandir}/man8/upclient.8 \
    %{buildroot}%{_mandir}/man8/upclient.afs.8

# fix generated files
perl -pi -e 's|%{_builddir}/%{name}-%{version}/src|../..|' \
    %{buildroot}%{_prefix}/src/libafs-%{version}-%{release}/src/config/Makefile.version

touch %{buildroot}%{_sysconfdir}/openafs/ThisCell
chmod 644 %{buildroot}%{_sysconfdir}/openafs/ThisCell

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%post client
%_post_service %{name}
if [ ! -e /afs ]; then
	mkdir /afs
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
%{_bindir}/afs_compile_et
%{_bindir}/afsmonitor
%{_bindir}/aklog
%{_bindir}/asetkey
%{_bindir}/bos
%{_bindir}/fs
%{_bindir}/klog
%{_bindir}/klog.krb
%{_bindir}/klog.krb5
%{_bindir}/knfs
%{_bindir}/kpasswd.afs
%{_bindir}/kpwvalid
%{_bindir}/livesys
%{_bindir}/pagsh.afs
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
%{_mandir}/man1/pagsh.afs.1*
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
%config(noreplace) %ghost %{_sysconfdir}/%{name}/ThisCell
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

%files -n %{develname}
%defattr(-,root,root)
%{multiarch_bindir}/rxgen
%{multiarch_bindir}/xstat_cm_test
%{multiarch_bindir}/xstat_fs_test
%{_bindir}/rxgen
%{_bindir}/xstat_cm_test
%{_bindir}/xstat_fs_test
%{_includedir}/*.h
%{_includedir}/afs
%{_includedir}/rx
%dir %{multiarch_includedir}/afs
%{multiarch_includedir}/afs/dirpath.h
%{multiarch_includedir}/afs/param.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/afs

%files -n dkms-%{module}
%defattr(-,root,root)
%{_prefix}/src/%{module}-%{dkms_version}

%files doc
%defattr(-,root,root)
%doc doc/LICENSE doc/pdf doc/txt doc/examples
%{_mandir}/man1/afs.1*
%{_mandir}/man1/afs_compile_et.1*
%{_mandir}/man1/aklog.1*
%{_mandir}/man1/cmdebug.1*
%{_mandir}/man1/copyauth.1*
%{_mandir}/man1/dlog.1*
%{_mandir}/man1/dpass.1*
%{_mandir}/man1/fs_apropos.1*
%{_mandir}/man1/fs_checkservers.1*
%{_mandir}/man1/fs_checkvolumes.1*
%{_mandir}/man1/fs_cleanacl.1*
%{_mandir}/man1/fs_copyacl.1*
%{_mandir}/man1/fs_cscpolicy.1*
%{_mandir}/man1/fs_diskfree.1*
%{_mandir}/man1/fs_examine.1*
%{_mandir}/man1/fs_exportafs.1*
%{_mandir}/man1/fs_flush.1*
%{_mandir}/man1/fs_flushall.1*
%{_mandir}/man1/fs_flushmount.1*
%{_mandir}/man1/fs_flushvolume.1*
%{_mandir}/man1/fs_getcacheparms.1*
%{_mandir}/man1/fs_getcalleraccess.1*
%{_mandir}/man1/fs_getcellstatus.1*
%{_mandir}/man1/fs_getclientaddrs.1*
%{_mandir}/man1/fs_getcrypt.1*
%{_mandir}/man1/fs_getfid.1*
%{_mandir}/man1/fs_getserverprefs.1*
%{_mandir}/man1/fs_help.1*
%{_mandir}/man1/fs_listacl.1*
%{_mandir}/man1/fs_listaliases.1*
%{_mandir}/man1/fs_listcells.1*
%{_mandir}/man1/fs_listquota.1*
%{_mandir}/man1/fs_lsmount.1*
%{_mandir}/man1/fs_memdump.1*
%{_mandir}/man1/fs_messages.1*
%{_mandir}/man1/fs_minidump.1*
%{_mandir}/man1/fs_mkmount.1*
%{_mandir}/man1/fs_monitor.1*
%{_mandir}/man1/fs_newalias.1*
%{_mandir}/man1/fs_newcell.1*
%{_mandir}/man1/fs_quota.1*
%{_mandir}/man1/fs_rmmount.1*
%{_mandir}/man1/fs_rxstatpeer.1*
%{_mandir}/man1/fs_rxstatproc.1*
%{_mandir}/man1/fs_setacl.1*
%{_mandir}/man1/fs_setcachesize.1*
%{_mandir}/man1/fs_setcbaddr.1*
%{_mandir}/man1/fs_setcell.1*
%{_mandir}/man1/fs_setclientaddrs.1*
%{_mandir}/man1/fs_setcrypt.1*
%{_mandir}/man1/fs_setquota.1*
%{_mandir}/man1/fs_setserverprefs.1*
%{_mandir}/man1/fs_setvol.1*
%{_mandir}/man1/fs_storebehind.1*
%{_mandir}/man1/fs_sysname.1*
%{_mandir}/man1/fs_trace.1*
%{_mandir}/man1/fs_uuid.1*
%{_mandir}/man1/fs_whereis.1*
%{_mandir}/man1/fs_whichcell.1*
%{_mandir}/man1/fs_wscell.1*
%{_mandir}/man1/klog.krb.1*
%{_mandir}/man1/klog.krb5.1*
%{_mandir}/man1/package_test.1*
%{_mandir}/man1/pts_adduser.1*
%{_mandir}/man1/pts_apropos.1*
%{_mandir}/man1/pts_chown.1*
%{_mandir}/man1/pts_creategroup.1*
%{_mandir}/man1/pts_createuser.1*
%{_mandir}/man1/pts_delete.1*
%{_mandir}/man1/pts_examine.1*
%{_mandir}/man1/pts_help.1*
%{_mandir}/man1/pts_interactive.1*
%{_mandir}/man1/pts_listentries.1*
%{_mandir}/man1/pts_listmax.1*
%{_mandir}/man1/pts_listowned.1*
%{_mandir}/man1/pts_membership.1*
%{_mandir}/man1/pts_quit.1*
%{_mandir}/man1/pts_removeuser.1*
%{_mandir}/man1/pts_rename.1*
%{_mandir}/man1/pts_setfields.1*
%{_mandir}/man1/pts_setmax.1*
%{_mandir}/man1/pts_sleep.1*
%{_mandir}/man1/pts_source.1*
%{_mandir}/man1/rxgen.1*
%{_mandir}/man1/symlink.1*
%{_mandir}/man1/symlink_list.1*
%{_mandir}/man1/symlink_make.1*
%{_mandir}/man1/symlink_remove.1*
%{_mandir}/man1/tokens.krb.1*
%{_mandir}/man1/vos_addsite.1*
%{_mandir}/man1/vos_apropos.1*
%{_mandir}/man1/vos_backup.1*
%{_mandir}/man1/vos_backupsys.1*
%{_mandir}/man1/vos_changeaddr.1*
%{_mandir}/man1/vos_changeloc.1*
%{_mandir}/man1/vos_clone.1*
%{_mandir}/man1/vos_convertROtoRW.1*
%{_mandir}/man1/vos_copy.1*
%{_mandir}/man1/vos_create.1*
%{_mandir}/man1/vos_delentry.1*
%{_mandir}/man1/vos_dump.1*
%{_mandir}/man1/vos_examine.1*
%{_mandir}/man1/vos_help.1*
%{_mandir}/man1/vos_listaddrs.1*
%{_mandir}/man1/vos_listpart.1*
%{_mandir}/man1/vos_listvldb.1*
%{_mandir}/man1/vos_listvol.1*
%{_mandir}/man1/vos_lock.1*
%{_mandir}/man1/vos_move.1*
%{_mandir}/man1/vos_offline.1*
%{_mandir}/man1/vos_online.1*
%{_mandir}/man1/vos_partinfo.1*
%{_mandir}/man1/vos_release.1*
%{_mandir}/man1/vos_remove.1*
%{_mandir}/man1/vos_remsite.1*
%{_mandir}/man1/vos_rename.1*
%{_mandir}/man1/vos_restore.1*
%{_mandir}/man1/vos_setfields.1*
%{_mandir}/man1/vos_shadow.1*
%{_mandir}/man1/vos_size.1*
%{_mandir}/man1/vos_status.1*
%{_mandir}/man1/vos_syncserv.1*
%{_mandir}/man1/vos_syncvldb.1*
%{_mandir}/man1/vos_unlock.1*
%{_mandir}/man1/vos_unlockvldb.1*
%{_mandir}/man1/vos_zap.1*
%{_mandir}/man1/xstat_cm_test.1*
%{_mandir}/man1/xstat_fs_test.1*
%{_mandir}/man5/AuthLog.5*
%{_mandir}/man5/AuthLog.dir.5*
%{_mandir}/man5/BackupLog.5*
%{_mandir}/man5/BosConfig.5*
%{_mandir}/man5/BosLog.5*
%{_mandir}/man5/CellAlias.5*
%{_mandir}/man5/CellServDB.5*
%{_mandir}/man5/FORCESALVAGE.5*
%{_mandir}/man5/FileLog.5*
%{_mandir}/man5/KeyFile.5*
%{_mandir}/man5/NetInfo.5*
%{_mandir}/man5/NetRestrict.5*
%{_mandir}/man5/NoAuth.5*
%{_mandir}/man5/SALVAGE.fs.5*
%{_mandir}/man5/SalvageLog.5*
%{_mandir}/man5/ThisCell.5*
%{_mandir}/man5/UserList.5*
%{_mandir}/man5/VLLog.5*
%{_mandir}/man5/VolserLog.5*
%{_mandir}/man5/afs.5*
%{_mandir}/man5/afs_cache.5*
%{_mandir}/man5/afs_volume_header.5*
%{_mandir}/man5/afsmonitor.5*
%{_mandir}/man5/afszcm.cat.5*
%{_mandir}/man5/bdb.DB0.5*
%{_mandir}/man5/butc.5*
%{_mandir}/man5/butc_logs.5*
%{_mandir}/man5/cacheinfo.5*
%{_mandir}/man5/fms.log.5*
%{_mandir}/man5/kaserver.DB0.5*
%{_mandir}/man5/kaserverauxdb.5*
%{_mandir}/man5/krb.conf.5*
%{_mandir}/man5/package.5*
%{_mandir}/man5/prdb.DB0.5*
%{_mandir}/man5/salvage.lock.5*
%{_mandir}/man5/sysid.5*
%{_mandir}/man5/tapeconfig.5*
%{_mandir}/man5/uss.5*
%{_mandir}/man5/uss_bulk.5*
%{_mandir}/man5/vldb.DB0.5*
%{_mandir}/man8/afsd.8*
%{_mandir}/man8/asetkey.8*
%{_mandir}/man8/backup.8*
%{_mandir}/man8/backup_adddump.8*
%{_mandir}/man8/backup_addhost.8*
%{_mandir}/man8/backup_addvolentry.8*
%{_mandir}/man8/backup_addvolset.8*
%{_mandir}/man8/backup_apropos.8*
%{_mandir}/man8/backup_dbverify.8*
%{_mandir}/man8/backup_deldump.8*
%{_mandir}/man8/backup_deletedump.8*
%{_mandir}/man8/backup_delhost.8*
%{_mandir}/man8/backup_delvolentry.8*
%{_mandir}/man8/backup_delvolset.8*
%{_mandir}/man8/backup_diskrestore.8*
%{_mandir}/man8/backup_dump.8*
%{_mandir}/man8/backup_dumpinfo.8*
%{_mandir}/man8/backup_help.8*
%{_mandir}/man8/backup_interactive.8*
%{_mandir}/man8/backup_jobs.8*
%{_mandir}/man8/backup_kill.8*
%{_mandir}/man8/backup_labeltape.8*
%{_mandir}/man8/backup_listdumps.8*
%{_mandir}/man8/backup_listhosts.8*
%{_mandir}/man8/backup_listvolsets.8*
%{_mandir}/man8/backup_quit.8*
%{_mandir}/man8/backup_readlabel.8*
%{_mandir}/man8/backup_restoredb.8*
%{_mandir}/man8/backup_savedb.8*
%{_mandir}/man8/backup_scantape.8*
%{_mandir}/man8/backup_setexp.8*
%{_mandir}/man8/backup_status.8*
%{_mandir}/man8/backup_volinfo.8*
%{_mandir}/man8/backup_volrestore.8*
%{_mandir}/man8/backup_volsetrestore.8*
%{_mandir}/man8/bos.8*
%{_mandir}/man8/bos_addhost.8*
%{_mandir}/man8/bos_addkey.8*
%{_mandir}/man8/bos_adduser.8*
%{_mandir}/man8/bos_apropos.8*
%{_mandir}/man8/bos_create.8*
%{_mandir}/man8/bos_delete.8*
%{_mandir}/man8/bos_exec.8*
%{_mandir}/man8/bos_getdate.8*
%{_mandir}/man8/bos_getlog.8*
%{_mandir}/man8/bos_getrestart.8*
%{_mandir}/man8/bos_help.8*
%{_mandir}/man8/bos_install.8*
%{_mandir}/man8/bos_listhosts.8*
%{_mandir}/man8/bos_listkeys.8*
%{_mandir}/man8/bos_listusers.8*
%{_mandir}/man8/bos_prune.8*
%{_mandir}/man8/bos_removehost.8*
%{_mandir}/man8/bos_removekey.8*
%{_mandir}/man8/bos_removeuser.8*
%{_mandir}/man8/bos_restart.8*
%{_mandir}/man8/bos_salvage.8*
%{_mandir}/man8/bos_setauth.8*
%{_mandir}/man8/bos_setcellname.8*
%{_mandir}/man8/bos_setrestart.8*
%{_mandir}/man8/bos_shutdown.8*
%{_mandir}/man8/bos_start.8*
%{_mandir}/man8/bos_startup.8*
%{_mandir}/man8/bos_status.8*
%{_mandir}/man8/bos_stop.8*
%{_mandir}/man8/bos_uninstall.8*
%{_mandir}/man8/bos_util.8*
%{_mandir}/man8/buserver.8*
%{_mandir}/man8/butc.8*
%{_mandir}/man8/fileserver.8*
%{_mandir}/man8/fms.8*
%{_mandir}/man8/fstrace.8*
%{_mandir}/man8/fstrace_apropos.8*
%{_mandir}/man8/fstrace_clear.8*
%{_mandir}/man8/fstrace_dump.8*
%{_mandir}/man8/fstrace_help.8*
%{_mandir}/man8/fstrace_lslog.8*
%{_mandir}/man8/fstrace_lsset.8*
%{_mandir}/man8/fstrace_setlog.8*
%{_mandir}/man8/fstrace_setset.8*
%{_mandir}/man8/ka-forwarder.8*
%{_mandir}/man8/kas.8*
%{_mandir}/man8/kas_apropos.8*
%{_mandir}/man8/kas_create.8*
%{_mandir}/man8/kas_delete.8*
%{_mandir}/man8/kas_examine.8*
%{_mandir}/man8/kas_forgetticket.8*
%{_mandir}/man8/kas_help.8*
%{_mandir}/man8/kas_interactive.8*
%{_mandir}/man8/kas_list.8*
%{_mandir}/man8/kas_listtickets.8*
%{_mandir}/man8/kas_noauthentication.8*
%{_mandir}/man8/kas_quit.8*
%{_mandir}/man8/kas_setfields.8*
%{_mandir}/man8/kas_setpassword.8*
%{_mandir}/man8/kas_statistics.8*
%{_mandir}/man8/kas_stringtokey.8*
%{_mandir}/man8/kas_unlock.8*
%{_mandir}/man8/kaserver.8*
%{_mandir}/man8/package.8*
%{_mandir}/man8/pt_util.8*
%{_mandir}/man8/ptserver.8*
%{_mandir}/man8/read_tape.8*
%{_mandir}/man8/restorevol.8*
%{_mandir}/man8/rmtsysd.8*
%{_mandir}/man8/salvager.8*
%{_mandir}/man8/upclient.afs.8*
%{_mandir}/man8/upserver.8*
%{_mandir}/man8/uss.8*
%{_mandir}/man8/uss_add.8*
%{_mandir}/man8/uss_apropos.8*
%{_mandir}/man8/uss_bulk.8*
%{_mandir}/man8/uss_delete.8*
%{_mandir}/man8/uss_help.8*
%{_mandir}/man8/vldb_convert.8*
%{_mandir}/man8/vlserver.8*
%{_mandir}/man8/volserver.8*
%{_mandir}/man8/vsys.8*
%{_mandir}/man8/xfs_size_check.8*
