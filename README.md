check_snailexec
===============
###### _Monitoring/Nagios plugin for working with SnailEXEC output_

Overview
========
The script treats the output of a command in a [SnailEXEC results file](https://github.com/Doctor-love/SnailEXEC) as a monitoring plugin.  
This method can be used to achive non-realtime checking of monitoring plugins for remote/isolated hosts.  

Installation
============
The plugin requires Python 2.7 or 2.6 with the "argparse" module installed.  

Example output
==============

```
$ ./check_snailexec.py --file "/path/to/results.json" --name "check_apt_updates"
APT WARNING: 136 packages available for upgrade (0 critical updates). |available_upgrades=136;;;0 critical_updates=0;;;0

$ echo "$?"
1
```

```
$ ./check_snailexec.py --file "/path/to/outdated_results.json" --name "check_load"
Result data for command "check_load" is too old (952 seconds)

$ echo "$?"
3
```
