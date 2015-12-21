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

Example use case
================
Imagine a scenario where you want to monitor a system that you can't reached directly.  
This could be due to strict security policies, badly configured routing or similar.  

But all hope is not lost - both the monitoring and target system can reach a internal FTP server:  

```

                 Commonly accessible network
                 +-------------------------+
                 |                         |
                 |  +-------------------+  |
            +------->     FTP server    <-------+
            |    |  +-------------------+  |    |
            |    |                         |    |
            |    +-------------------------+    |
            |                                   |
            |                 X                 |
+-------------------------+   X   +--------------------------+
|           |             |   X   |             |            |
|  +--------+----------+  |   X   |  +----------+--------+   |
|  | Monitoring system |  |   X   |  |   Target system   |   |
|  +-------------------+  |   X   |  +-------------------+   |
|                         |   X   |                          |
+-------------------------+   X   +--------------------------+
    Isolated network A        X        Isolated network B

```

The target system can run a SnailEXEC job with appropriate check plugins,  
triggered every five minutes by something like cron and upload the  
results file to the commonly accessible FTP server.  

A script on the monitoring system downloads the results file on a scheduled basis and  
check_snailexec treats each result in the results file as a check result!  


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
