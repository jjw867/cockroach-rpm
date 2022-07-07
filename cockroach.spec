%undefine _disable_source_fetch

Name:             cockroach
Version:          22.1.2
Release:          1%{?dist}
Summary:          The open source, cloud-native distributed SQL database.

License:          CockroachDB Community License Agreement (https://raw.githubusercontent.com/cockroachdb/cockroach/master/licenses/CCL.txt)
URL:              https://www.cockroachlabs.com/
Group:            Applications/Database
Vendor:           Cockroach Labs
Source0:          https://binaries.cockroachdb.com/%{name}-v%{version}.linux-amd64.tgz
Source1:          https://raw.githubusercontent.com/jjw867/cockroach-sos-plugin/main/cockroach.py
Source2:          50-cockroach
Source3:          cockroach.conf
Source4:          cockroach-logs.yaml
Source5:          cockroach-server.xml
Source6:          cockroach-ui.xml
Prefix:           %{_prefix}
Packager:         Jeffrey White <jeffreyw@cockroachlabs.com>

Requires:         chrony
Requires:         firewalld
Requires:         sos >= 3.7
Requires:         python3
Requires:         openssh-clients
Requires(pre):    shadow-utils
Requires(pre):    /usr/sbin/useradd
Requires(post):   systemd
Requires(post):   firewalld
Requires(preun):  systemd
Requires(postun): systemd
Requires(postun): firewalld

%description
CockroachDB is a distributed SQL database built on a transactional and strongly-consistent key-value store. It scales horizontally; survives disk, machine, rack, and even datacenter failures with minimal latency disruption and no manual intervention; supports strongly-consistent ACID transactions; and provides a familiar SQL API for structuring, manipulating, and querying data.


%undefine _missing_build_ids_terminate_build
%global debug_package %{nil}

%prep
%setup -q -n %{name}-v%{version}.linux-amd64

%build


%install
#Filesystem
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/certs
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/scripts
install -d $RPM_BUILD_ROOT/%{_localstatedir}/lib/%{name}
install -d $RPM_BUILD_ROOT/%{_localstatedir}/log/%{name}
install -d $RPM_BUILD_ROOT/%{_localstatedir}/run/%{name}

mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/lib64
mkdir -p $RPM_BUILD_ROOT/usr/share/bash-completion/completions/cockroach
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/firewalld/services
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sudoers.d

mkdir -p $RPM_BUILD_ROOT/usr/lib/python3.6/site-packages/sos/report/plugins
cp $RPM_SOURCE_DIR/cockroach.py $RPM_BUILD_ROOT/usr/lib/python3.6/site-packages/sos/report/plugins

cp $RPM_BUILD_DIR/%{name}-v%{version}.linux-amd64/cockroach $RPM_BUILD_ROOT/usr/bin/cockroach
cp $RPM_BUILD_DIR/%{name}-v%{version}.linux-amd64/lib/libgeos_c.so $RPM_BUILD_ROOT/usr/lib64
cp $RPM_BUILD_DIR/%{name}-v%{version}.linux-amd64/lib/libgeos.so $RPM_BUILD_ROOT/usr/lib64
cp $RPM_SOURCE_DIR/cockroach-server.xml $RPM_BUILD_ROOT/%{_sysconfdir}/firewalld/services
cp $RPM_SOURCE_DIR/cockroach-ui.xml $RPM_BUILD_ROOT/%{_sysconfdir}/firewalld/services
cp $RPM_SOURCE_DIR/cockroach.conf $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/%{name}.conf
cp $RPM_SOURCE_DIR/cockroach-logs.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}
cp $RPM_SOURCE_DIR/cockroach.service $RPM_BUILD_ROOT/%{_unitdir}
cp $RPM_SOURCE_DIR/50-cockroach $RPM_BUILD_ROOT/%{_sysconfdir}/sudoers.d
cp -R $RPM_SOURCE_DIR/scripts $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}

# Install man pages
$RPM_BUILD_ROOT/usr/bin/cockroach gen man
man=$(dirname %{buildroot}%{_mandir})
for page in man/man?/*; do
    install -Dpm644 $page $man/$page
done

# Bash autocomplete
$RPM_BUILD_ROOT/usr/bin/cockroach gen autocomplete
cp $RPM_BUILD_DIR/%{name}-v%{version}.linux-amd64/cockroach.bash $RPM_BUILD_ROOT/usr/share/bash-completion/completions/cockroach

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%pre
getent group %{name} &> /dev/null || \
groupadd -r %{name} &> /dev/null
getent passwd %{name} &> /dev/null || \
useradd -r -m -g %{name} -d /home/%{name} -s /bin/bash \
-c 'Cockroach Database Server' %{name} &> /dev/null
exit 0

%post
#Reload the firewall to pickup new rules
systemctl reload firewalld
%systemd_post %{name}.service
echo -e "set -o allexport\nsource /etc/cockroach/cockroach.conf\nset + allexport\n" >> /home/%{name}/.bashrc

#Block cockroach user from loging in remotely
echo  "DenyUsers cockroach"  >>/etc/ssh/sshd_config
systemctl restart sshd

%preun
%systemd_preun %{name}.service

%postun
systemctl reload firewalld
%systemd_postun_with_restart %{name}.service

#Delete cockroach user entry
sed -i '/DenyUsers cockroach/d' /etc/ssh/sshd_config
systemctl restart sshd

%files
%defattr(0755, root, root) 
%dir %attr(0750, cockroach, cockroach) %{_localstatedir}/log/%{name}
%dir %attr(0750, cockroach, cockroach) %{_sharedstatedir}/%{name}
%dir %attr(0750, cockroach, cockroach) %{_sysconfdir}/%{name}
%config(noreplace) %dir %attr(0750, cockroach, cockroach) %{_sysconfdir}/%{name}/certs
%dir %attr(0755, cockroach, cockroach) %{_localstatedir}/run/%{name}
/usr/bin/%{name}
/usr/lib64/libgeos_c.so
/usr/lib64/libgeos.so
/usr/lib64/libgeos_c.so.1
/etc/firewalld/services/*
/etc/sudoers.d/50-cockroach
%{_unitdir}/%{name}.service
%attr(0644, root, root) %{_mandir}/man1/%{name}*
%dir %attr(0755, cockroach, cockroach) %{_sysconfdir}/%{name}/scripts
%attr(0755, cockroach, cockroach) %{_sysconfdir}/%{name}/scripts/*
%config(noreplace) %attr(0644, cockroach, cockroach) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %attr(0644, cockroach, cockroach) %{_sysconfdir}/%{name}/cockroach-logs.yaml
/usr/share/bash-completion/completions/%{name}/%{name}.bash
%attr(0644, root, root) /usr/lib/python3.6/site-packages/sos/report/plugins/cockroach.py
%exclude %dir /usr/lib/python3.6/site-packages/sos/report/plugins/__pycache__
%exclude /usr/lib/python3.6/site-packages/sos/report/plugins/__pycache__/*

%doc

%changelog
* Tue Jun 21 2022 Jeff White <jeffreyw@cockroachlabs.com>
  - Initial version
