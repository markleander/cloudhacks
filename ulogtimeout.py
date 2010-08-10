#!/usr/bin/python
#
# ulogtimeout.py - run command when no iptables ULOG action for some time
#
# SYNOPSIS: python ulogtimeout.py <timeout> <command> [<lockport>]
#
# This script will execute a shell command when there has been no netlink
# ULOG messages as broadcasted by iptables for a specified amount of time.
#
# timeout  - time in seconds to wait for ULOG messages before running command
# command  - shell command line passed directly to system()
# lockport - If specified, the script will listen on this port (TCP). This
#            serves as a simple locking mechanism preventing two instances of
#            the script from running simultaneously.
#
# This must be run as root to work as listening on netlink multicast groups
# requires CAP_NET_ADMIN.
#
# EXAMPLE: Shut down host when no incoming SSH traffic for about 20 minutes
#
# # iptables -I INPUT -m limit --limit 1/minute -p tcp --dport 22 -j ULOG
# # python ulogtimeout.py 1200 'shutdown -h +5' 7777 &
#
# Copyright 2010 topicbranch.net. All rights reserved.
#

import os
import sys
import socket
import struct
import collections

def ulogsock():
    nl_groups = 0xffff
    sk = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, socket.NETLINK_NFLOG)
    sk.bind((0, nl_groups))
    return sk

def main():
    timeout = float(sys.argv[1])
    cmd = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])
        sklock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sklock.bind(('', port))

    sk = ulogsock()
    sk.settimeout(timeout)
    while True:
        try:
            x = sk.recv(4096)
        except socket.timeout:
            print 'ULOG TIMEOUT. Running %s' % cmd
            os.system(cmd)

if __name__ == '__main__':
    main()
