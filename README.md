# Overview

This repository has all of the pieces needed to build a package for [CockroachDB](https://github.com/cockroachdb/cockroach), except for the [SOS](https://github.com/sosreport/sos) plugin.  The SOS plugin can be found here.  https://github.com/jjw867/cockroach-sos-plugin.

Currently, this is RPM has only been tested on RHEL 8.6 and Centos 8 (.6 ish stream).

## Prepare

Install the packages needed to build and manipulate packages.

- `sudo yum install -y rpm-build rpmdevtools mock`

## Building

Do not run these steps as root.  Never build packages as root.  You have been warned.

The spec file will pull the cockroach binary and the SOS plugin file.

1. `git clone https://github.com/jjw867/cockroach-rpm`
2. `cd cockroach-rpms`
3. `rpmdev-setuptree`
4. `spectool -g cockroach.spec`
5. `rpmbuild -ba --define "_sourcedir $(pwd)" --define "_srcrpmdir $(pwd)" cockroach.spec`
6. `sudo mock <the srpm from step 5>`

## Design of the RPM

Cockroach is by design made to be simple to install and run.  It's a single binary file.  

To run on a typical operating system, some bits need to be added allow a more consistent deployment.  The overall goal of the RPM is to lower the friction to getting a cockroach database up and running.  It is also designed to help put various pieces in sane places.  Some of the pieces will be useful for mature operations teams to use not necessarily using the package.

Things the package does:
- Puts the cockroach supplied libgeos library files into /usr/local/lib/cockroach.
- Create the manual pages, and put them in man1 section.
- Create the bash autocompletion script and put it in /usr/share/bash-completion/completions/cockroach.
- Create a cockroach user and cockroach group.
- Create a /home/cockroach location for the cockroach user, a place to park scripts etc.  It also helps to keep file ownership correct.  The idea is to su - cockroach to do cockroach database things.  This also simplifies security in environment where the DBA's to not have root priviledges.  
- Allow the cockroach user in sudo start, stop and reload the database with systemctl.  
- Block the cockroach user from being able to login from ssh.
- Add firewalld xml file for the standard server port and standard user port.
- Create an /etc/cockroach directory for storing important bits.
- Create a /var/log/cockroach for cockroach to put logs.
- Create a /var/lib/cockroach for cockroach database files to live.
- Create (and recreate if needed) a /var/run/cockroach directorty to put a file with the PID of the process.

### /etc/cockroach

This directory holds the configuration file (below), the log configuration yaml for the cockroach binary, a protected subdirectory for key certificates and a scripts directory.

### /etc/cockroach/cockroach.conf

This file holds environment variables that drive a number of the scripts.  The idea is that the config file has sane values and gives on place to change them.

### /etc/cockroach/certs

A protected place to put our important cryto keys for the database.
### Scripts /etc/cockroach/scripts

Some of these scripts are fairly obvious and possibly unnecessary.  But they might save some time in getting initially setup.

- cockroach-create-ca.sh - you only run this once and replicate the CA to all of the other nodes
- cockroach-create-node.sh - create the keys for this node, need to create or have the CA first
- cockroach-create-rootuser.sh - create keys for the initial root user, but not a password
- cockroach-init-db.sh - initialize a multi-node database, not needed for single node
- cockroach-enable-firewall.sh - the installation does not by default open up the firewall ports, because perhaps you don't want them enabled

- cockroach-start.sh - this script is called by the systemd service file, because systemd does not do shell expansion
- cockroach-stop.sh - gracefully stops the database instance

## SystemD Service

We really try to make sure we have the time synchronized.  In the systemd service file we check and in the shell scripted called by the systemd service file.  We will also ensure we have enough file handles for our cockroach process.

## Start/Stop cockroach service

From the cockroach user account:
```
[root@crdb1 cockroach]# su - cockroach
[cockroach@crdb1 ~]$ id
uid=988(cockroach) gid=983(cockroach) groups=983(cockroach) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[cockroach@crdb1 ~]$ sudo systemctl start cockroach
[cockroach@crdb1 ~]$ sudo systemctl status cockroach
● cockroach.service - Cockroach SQL Database Server
   Loaded: loaded (/usr/lib/systemd/system/cockroach.service; disabled; vendor preset: disabled)
   Active: active (running) since Fri 2022-07-08 10:03:38 CDT; 31min ago
     Docs: https://www.cockroachlabs.com/docs,
           man:cockroach(1)
  Process: 45073 ExecStart=/etc/cockroach/scripts/cockroach-start.sh (code=exited, status=0/SUCCESS)
  Process: 45071 ExecStartPre=/bin/chown -R cockroach:cockroach /var/run/cockroach (code=exited, status=0/SUCCESS)
  Process: 45069 ExecStartPre=/bin/mkdir -p /var/run/cockroach (code=exited, status=0/SUCCESS)
 Main PID: 45094 (cockroach)
    Tasks: 10 (limit: 23642)
   Memory: 302.6M
   CGroup: /system.slice/cockroach.service
           └─45094 /usr/bin/cockroach start --certs-dir=/etc/cockroach/certs --store=/var/lib/cockroach --cache=0.25 --max-sql-memory=0.25 --log-config-file=/etc/cockroach/cockroa>

Jul 08 10:03:38 crdb1.home.white.nu systemd[1]: Starting Cockroach SQL Database Server...
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: *
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * INFO: initial startup completed.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Node will now attempt to join a running cluster, or wait for `cockroach init`.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Client connections will be accepted after this completes successfully.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Check the log file(s) for progress.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: *
Jul 08 10:03:38 crdb1.home.white.nu systemd[1]: Started Cockroach SQL Database Server.
[cockroach@crdb1 ~]$ sudo systemctl stop cockroach
[cockroach@crdb1 ~]$ sudo systemctl status cockroach
● cockroach.service - Cockroach SQL Database Server
   Loaded: loaded (/usr/lib/systemd/system/cockroach.service; disabled; vendor preset: disabled)
   Active: inactive (dead)
     Docs: https://www.cockroachlabs.com/docs,
           man:cockroach(1)

Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Node will now attempt to join a running cluster, or wait for `cockroach init`.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Client connections will be accepted after this completes successfully.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: * Check the log file(s) for progress.
Jul 08 10:03:38 crdb1.home.white.nu cockroach[45094]: *
Jul 08 10:03:38 crdb1.home.white.nu systemd[1]: Started Cockroach SQL Database Server.
Jul 08 10:36:58 crdb1.home.white.nu systemd[1]: Stopping Cockroach SQL Database Server...
Jul 08 10:36:58 crdb1.home.white.nu cockroach[45094]: initiating graceful shutdown of server
Jul 08 10:37:01 crdb1.home.white.nu cockroach[45094]: server drained and shutdown completed
Jul 08 10:37:01 crdb1.home.white.nu systemd[1]: cockroach.service: Succeeded.
Jul 08 10:37:01 crdb1.home.white.nu systemd[1]: Stopped Cockroach SQL Database Server.

```

## Accessing cockroach systemd logs

```
[cockroach@crdb1 ~]$ sudo journalctl -t cockroach
-- Logs begin at Thu 2022-07-07 15:41:11 CDT, end at Fri 2022-07-08 10:45:00 CDT. --
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: *
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: * INFO: initial startup completed.
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: * Node will now attempt to join a running cluster, or wait for `cockroach init`.
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: * Client connections will be accepted after this completes successfully.
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: * Check the log file(s) for progress.
Jul 08 10:03:06 crdb1.home.white.nu cockroach[10761]: *
```

## To Do

- [ ] Fix it so it's not 22.1.2 specific.
- [ ] Add cgroup, might be useful for segregating metrics.
- [ ] Support running multiple instances for NUMA.  And no, turing off NUMA in the BIOS will not make NUMA go away.
- [ ] Maybe get a script to distribute keys to new nodes.  This might really be an exercise for the end user's environment.
- [ ] Improve the stop process, I have concerns about going too fast to shutdown.
- [ ] Script to retire this node?
- [ ] SELinux support.
- [ ] We assume we're using chrony for time synchronization.  It's possible NTP is being used.  We should also whine about using systemd for time sync instead of chrony or NTP.
- [ ] Eventually make this build process part of the factory that builds cockroach releases (* paging engineering *).
- [ ] Test on RHEL 9 and RHEL 9 variants.
- [ ] Test on more RHEL 8 variants.
- [ ] Test on Fedora.
- [ ] Make the SOS plugin its own package.

## Issues

- [ ] The systemd service file needs more testing for edge cases.
- [ ] Restart on failure in the systemd service file is either a bad idea or a good idea.
- [ ] Only tested on RHEL 8 and Centos Stream 8.

## Testing needed

- [ ] More testing is needed, you've been warned.

## Possible future changes/fixes

- [ ] SOS Package probably should not be a requirement.
- [ ] Make potentially bad assumptions about where the SOS plugin goes.
- [ ] Perhaps /etc/cockroach might be world readable.
- [ ] Better edge case detections.
- [ ] There are a lot of possible more customized configurations that are easier made by simply editing the files.
- [ ] Backporting to support 21.2, doing this might not be worth the effort.
- [ ] Need a Debian/Ubuntu .deb package, but that is for another repository.
