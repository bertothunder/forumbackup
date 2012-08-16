#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import *  
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
       raise NoSectionError('given section %(name)s does not exist in credentials file' % {'name': section})
  
def getVal(config, section, item):
    # First check we are working with the correct object type
    assert type(config) == ConfigParser
    if config_.section.has_option(item):
        return config_.get(section, item)
    else:
        raise NoOptionError('option %(name)s does not exist in credentials file' % {'name': item})
     
if __name__ == '__main__':
    assert getCredentials('clubsuperblackbird') == True
    print globals_.USERNAME, globals_.PASSWD
