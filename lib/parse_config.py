# -*- coding: utf-8 -*-
import os
import logging
from ConfigParser import SafeConfigParser

def parse(file):
    config = SafeConfigParser()
    config.read(file)
    root = os.path.dirname(os.path.dirname(__file__))
    config.set('general', 'static_path', os.path.join(root, 'static'))
    config.set('general', 'template_path', os.path.join(root, 'template'))
    config.set('general', 'log_function', os.path.join(root, 'lib/log.py'))
    for s in config.sections():
        if s.startswith('log:'):
            l = getattr(logging, config.get(s, 'level'))
            config.set(s, 'level', str(l))
    return config

if __name__ == '__main__':
    parse('../config.conf')
