# -*- coding: utf-8 -*-

class Source(object):
    def __init__(self, config={}):
        self.config = config

    def ips(self):
        return []

    def urls(self):
        return []

    def ip_port_pairs(self):
        return []


