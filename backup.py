#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mechanize
import cookielib
import re
import sys
import getopt
from config import *
from globals import * 
from BeautifulSoup import *
from urllib2 import HTTPError

def setupBrowser():
    # Setup a browser instance...
    browser_ = mechanize.Browser()
    browser_.set_handle_redirect(False)
    browser_.set_handle_robots(False)

    # Add necessary headers for User-agent
    browser_.addheaders = [('User-agent', globals.USERAGENT)]

    return browser_

def setupCookies(browser):
    # Setup a cookie handler and attach to browser
    cookies = cookielib.LWPCookieJar()
    browser.set_cookiejar(cookies)

def Login(browser, username, passwd):
    result = False
    try:
        # Open forum page
        browser.open(globals.URL)

        # Once opened the page, look for the login form and fill it
        browser.select_form('form_login');
        browser['username']= username
        browser['password'] = passwd
        browser['autologin'] = ['on']
        # And submit. We expect a 302 redirection status after POSTing the
        # form for login...
        browser.submit()
    except HTTPError, e:
        # We are expecting a 302 status code after login, that means in this case
        # everything wents ok 
        if e.code == 302:
            # Move back to main URL
            result = True
        else:
            raise HTTPError
        
    return result


# Return list of sections in a list of tuples, including calculated index...
def getSections(html, debug = False):
    # Feed beautifulSoup with the read html
    # Read sectionsl
    soup = BeautifulSoup(html)
    sectionNum = 0
    sectionList = []
    for link in soup.findAll('a', attrs={'class':'forumtitle'}):
        sectionNum += 1
        sectionList.append((sectionNum, link.text, link['href']))

    if (debug):
        print "Número de secciones encontradas: ", sectionNum
        print "==============================================="
        print "SQL:"
        for idx, name, url in sectionList:
            print idx, '.- INSERT INTO sections(NAME, URL) VALUES("%(name)s", "%(url)s");' % \
                  {'name': name, 'url': url}

    return sectionList


# get TID, will be used later on for admin purpouses
def getAdminTid(html):
    _tid = ''
    adminref = '^/admin/index.forum\?part=admin\&tid=';
    soup = BeautifulSoup(html)
    # Find exact link (a href=) that begins with above href, will contain TID at the end
    for link in soup.findAll('a', attrs={'href':re.compile(adminref)}):
        tid = link['href']
        # TID value will be after last = (first from right side)
        tid = tid[tid.rindex('=')+1:]
        _tid = tid

    return _tid
    

def backup(section):
    # Setup credentials from config file
    getCredentials(section)

    # Obtain a browser instance finely setup
    browser = setupBrowser()

    # Prepare cookies handling mechanism
    setupCookies(browser)

    # Login and get initial webpage for admin user
    # NOTE: assert will stop exec if login failed
    Login(browser, globals.USERNAME, globals.PASSWD)
    
    # Cool! login was fine, move back to main URL and get html
    response = browser.open(globals.URL)
    html = response.read()

    # Get main sections from given html
    sections = getSections(html)
    
    # Get administration TID (and assert value is valid!)
    tid = getAdminTid(html)
    assert tid != ''


# Get list of messages from a given section
#def getMessagesList(browser, section

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Must give a section name from your credentials file'    
        sys.exit(2)
    backup(sys.argv[1])
