#!/bin/bash

cd /Users/lucernae/Scripts

sudo ./local_resolver.py en0 /<your conf location>/dnsmasq.conf /etc/resolver/test test
docker restart dnsmasq
