#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# dpid - DPI solution based on OpenBSD, pf, relayd and exabgp
# Copyright (C) 2017 Sergey Simonenko <gforgx@fotontel.ru>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time

import dpilib.sources
import dpilib.routers

import jsoncfg

config = jsoncfg.load_config('dpid.conf')

# Init Router objects

routers_list = []

for router in config.routers:
        module = router.module()

        if hasattr(dpilib.routers, module):
            router_class = getattr(dpilib.routers, module).Router

            router_config = {}
            for option in router_class.config:
                router_config[option] = getattr(router, option).__call__(router_class.config[option])

            routers_list.append(router_class(router_config))

# Init Source objects
sources_list = []

for source in config.sources:
        module = source.module()

        if hasattr(dpilib.sources, module):
            source_class = getattr(dpilib.sources, module).Source

            source_config = {}
            for option in source_class.config:
                source_config[option] = getattr(source, option).__call__(source_class.config[option])

            sources_list.append(source_class(source_config))

print routers_list
print sources_list


all_ips = []

if os.path.exists('/var/tmp/dpid.list'):
    all_ips.extend([ip.strip() for ip in open('/var/tmp/dpid.list').readlines()])

while 1:

    for ip in all_ips:
            print ip
            open(config.exabgp_pipe('/var/run/exabgp.cmd'), 'w').write('withdraw route %s next-hop self community 65535:65281\n' % ip)

    for source in sources_list:
        for router in routers_list:

            ips_to_block = source.ips_to_block()
            ips_to_divert = source.ips_to_divert()
            ip_port_pairs = source.ip_port_pairs_to_block()

            https_ips_to_block = [pair[0] for pair in ip_port_pairs]

        # For exabgp
        all_ips = list(set(ips_to_block + ips_to_divert + https_ips_to_block))
        
        
        open('/var/tmp/dpid.list', 'w').write('\n'.join(all_ips))

        for ip in all_ips:
            open(config.exabgp_pipe('/var/run/exabgp.cmd'), 'w').write('announce route %s next-hop self community 65535:65281 local-preference 205\n' % ip)

        router.block_ips(ips_to_block)
        router.block_ip_port_pairs(ip_port_pairs)
        router.divert_ips(ips_to_divert)
        router.block_urls(source.urls_to_block())


    time.sleep(config.sleep_time())

