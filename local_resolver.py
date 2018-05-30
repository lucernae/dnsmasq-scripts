#!/usr/bin/env python
# coding=utf-8

import fileinput
import re
import netifaces as ni
import sys


def find_interface_address(ifname):
    try:
        return ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    except:
        return None


def replace_resolver_entry(dnsmasq_conf_loc, resolver_loc, domain_name, addr):

    pattern = r"^address=/{domain}/(?P<addr>[\d.]+)$".format(
        domain=domain_name)
    replacement = r"address=/{domain}/{addr}".format(
        domain=domain_name,
        addr=addr)

    conf_file = fileinput.input(
            files=(dnsmasq_conf_loc, ),
            inplace=True,
            backup='.bak')

    for line in conf_file:
        line = re.sub(pattern, replacement, line)
        print line,

    conf_file.close()

    with open(resolver_loc, 'w') as resolver:
        resolver.write('nameserver 127.0.0.1\n')


if __name__ == '__main__':
    ifname = sys.argv[1]
    dnsmasq_loc = sys.argv[2]
    resolver_loc = sys.argv[3]
    domain_name = sys.argv[4]

    addr = find_interface_address(ifname)
    replace_resolver_entry(dnsmasq_loc, resolver_loc, domain_name, addr)
