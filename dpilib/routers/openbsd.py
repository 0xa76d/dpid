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
import base

class Router(base.Router):
    config = {
        'pf_divert_table_file': '/etc/pf.divert',
        'pf_block_table_file': '/etc/pf.block',
        'pf_block_https_table_file': '/etc/pf.block_https',
        'relayd_url_filter_file': '/etc/relayd.filter'
        }

    def block_ips(self, ips):
        open(self.config['pf_block_table_file'], 'w').write('\n'.join(ips))

        return os.system('pfctl -f /etc/pf.conf')

    def divert_ips(self, ips):
        open(self.config['pf_divert_table_file'], 'w').write('\n'.join(ips))

        return os.system('pfctl -f /etc/pf.conf')

    def block_ip_port_pairs(self, pairs):
        open(self.config['pf_block_https_table_file'], 'w').write('\n'.join((i[0] for i in pairs)))

    def block_urls(self, urls):
        open(self.config['relayd_url_filter_file'], 'w').write('\n'.join(urls))
        os.system('/usr/sbin/relayctl load /etc/relayd.conf')
