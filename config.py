#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser, NoSectionError
from globals import globals

globals_ = globals

def getCredentials(section):
    config_ = ConfigParser()
    config_.readfp(open('.credentials'))
    if config_.has_section(section):
        globals_.USERNAME = config_.get(section, 'username')
        globals_.PASSWD = config_.get(section, 'password')
        globals_.URL = config_.get(section, 'url')
    else:
        raise NoSectionError('given section %(name)s does not exist in credentials file' % { 'name': section })
     
if __name__ == '__main__':
    assert getCredentials('clubsuperblackbird') == True
    print globals_.USERNAME, globals_.PASSWD
