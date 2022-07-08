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

Cockroach is by design made to be simple to install and run.  It's a single binary file.  To run on a typical operating system, some bits need to be added allow faster and perhaps a more consistent deployment.  The overall goal is to lower the friction to getting a database up and running.  Some of the pieces will be useful for mature operations teams to use.

Things the package does:
- Puts the cockroach supplied libgeos library files into /usr/local/lib/cockroach.
- Create the manual pages, and put them in man1 section.
- Create the bash autocompletion script and put it in /usr/share/bash-completion/completions/cockroach.
- Create a cockroach user and cockroach group.
- Create a /home/cockroach location for the cockroach user, a place to park scripts etc.  It also helps to keep file ownership correct.
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

We really try to make sure we have the time synchronized.  In the systemd service file we check and in the shell scripted called by the systemd service file.  

## Start/Stop cockroach service

## Accessing cockroach systemd logs

## To Do

- [ ] Fix it so it's not 22.1.2 specific.
- [ ] Add cgroup, might be useful for segregating metrics.
- [ ] Support running multiple instances for NUMA.  And no, turing it off in the BIOS will not resolve NUMA being a performance hit.
- [ ] Maybe get a script to distribute keys to new nodes, really an exercise for the end user's environment.
- [ ] Improve the stop process, I have concerns about going too fast to shutdown.
- [ ] Script to retire this node?
- [ ] SELinux support
- [ ] We assume we're using chrony for time synchronization.  It's possible NTP is being used.  We should also whine about using systemd for time sync.
- [ ] Eventually make this build process part of the factory that builds cockroach releases (* paging engineering *)
- [ ] Test on RHEL 9 and RHEL 9 variants
- [ ] Test on more RHEL 8 variants
- [ ] Test on Fedora

## Issues

- [ ] The systemd service file needs more testing for edge cases.
- [ ] Restart on failure in the systemd service file is either a bad idea or a good idea.
- [ ] Something odd with the cockroach binary and the shell environment to get an SQL prompt is going sideways.  Need to investigate.
- [ ] Only tested on RHEL 8 and Centos Stream 8

## Testing needed


## Possible future changes/fixes

- [ ] SOS Package probably should not be a requirement.
- [ ] Make potentially bad assumptions about where the SOS plugin goes.
- [ ] Perhaps /etc/cockroach might be world readable.
- [ ] Better edge case detections.
- [ ] There are a lot of possible more customized configurations that are easier made by simply editing the files.
- [ ] Backporting to support 21.2, doing this might not be worth the effort.


