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

import base

import xml.etree.ElementTree

class Source(base.Source):
    config = {
            'dump_xml_path': '/root/dump.xml',
            }

    def parse(self):
        return self.__parse()

    def __parse(self):
        records = []

        tree = xml.etree.ElementTree.parse(self.config['dump_xml_path'])
        
        root = tree.getroot()
        
        for content in tree.getroot():
            if 'blockType' in content.attrib:
                block_type = content.attrib['blockType']
            else:
                block_type = 'default'

            data = {}

            for record in content:
                if record.tag != 'decision':
                    data.setdefault(record.tag, [])

                    data[record.tag].append(record.text)

            records.append((block_type, data))

        return records

    def ips_to_divert(self):
        ips = []

        for (block_type, data) in self.__parse():
            if block_type in ('default', 'domain', 'domain-mask'):
                if 'ip' in data:
                    ips.extend([i + '/32' for i in data['ip']])

        return ips

    def ips_to_block(self):
        ips = []

        for (block_type, data) in self.__parse():
            if block_type == 'ip':
                if 'ip' in data:
                    ips.extend([i + '/32' for i in data['ip']])
                if 'ipSubnet' in data:
                    ips.extend(data['ipSubnet'])
                

        return ips

    def ip_port_pairs_to_block(self):
        pairs = []
        for (block_type, data) in self.__parse():
            if block_type == 'default':
                for url in data['url']:
                    if url.startswith('https://'):
                        for ip in data['ip']:
                            pairs.append((ip, 443))

                        break

            if block_type in ('domain', 'domain-mask'):
                for ip in data['ip']:
                    pairs.append((ip + '/32', 443))

        return pairs

    def urls_to_block(self):
        urls = []

        for (block_type, data) in self.__parse():
            if block_type in ('domain', 'domain-mask'):
                for domain in data['domain']:
                    urls.append(domain.encode('utf-8') + '/')

            if block_type == 'default':
                for url in data['url']:
                    if url.startswith('http://'):
                        urls.append(url[7:].encode('utf-8'))

        return urls

if __name__ == '__main__':
    s = Source({'dump_xml_path': '/root/dump.xml'})


    print s.ips_to_divert()

