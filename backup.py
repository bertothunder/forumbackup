#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mechanize
import cookielib
import sys
from config import *
from globals import * 
from BeautifulSoup import *
from urllib2 import HTTPError


# Setup a mechanize browser instance and all the properties we need
def setupBrowser():
    # Setup a browser instance...
    browser_ = mechanize.Browser()
    browser_.set_handle_redirect(False)
    browser_.set_handle_robots(False)
    browser_.set_debug_redirects(True)

    # Add necessary headers for User-agent
    browser_.addheaders = [('User-agent', globals.USERAGENT)]

    return browser_


# Prepare and set a cookieJar object to given browser object
# for cookie signal handling during navigation
def setupCookies(browser):
    # Setup a cookie handler and attach to browser
    cookies = cookielib.LWPCookieJar()
    browser.set_cookiejar(cookies)



# Performs login over the browser page and check redirect from foroactivo
# has been received (that means login was succesful)
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

    print _tid
    return _tid



# Return list of sections in a list of tuples, including calculated index...
def getSections(html, debug = False):
    # Feed beautifulSoup with the read html
    # Read sectionsl
    soup = BeautifulSoup(html)
    sectionNum = 0
    sectionList = []
    for link in soup.findAll('a', attrs={'class':'forumtitle'}):
        sectionNum += 1
        sectionList.append((sectionNum, link.string, link['href']))

    if (debug):
        print "Número de secciones encontradas: ", sectionNum
        print "==============================================="
        print "SQL:"
        for idx, name, url in sectionList:
            print idx, '.- INSERT INTO sections(NAME, URL) VALUES("%(name)s", "%(url)s");' % \
                  {'name': name, 'url': url}

    return sectionList


    
# Get list of messages in a give page
def getMessagesInPage(html, idx, messages, page):
    soup = BeautifulSoup(html)

    print 'Recorriendo mensaje en página ',page,'!'
    msghref = '^/t\d+-\w+.*$'
    # Find the divs containing the messages
    for link in soup.findAll('a', attrs={'class':'topictitle',
                                         'href':re.compile(msghref)}):
        print "Añadiendo mensaje ",link.string, "con url", link['href']
        messages.append((idx,link.string,link['href'],page))


# Get list of messages from a given section
def getMessagesInSection(browser, idx, url):
    # Reset browser to clean it up
    browser.set_handle_redirect(True)
       
    # Compose and open section URL
    sectionUrl = '%(base)s%(section)s' %  {'base': globals.URL, \
                                            'section': url}
    print sectionUrl
    sectionResponse = browser.open(sectionUrl)

    # Setup some variables for later use
    messages = []
    totalpages = 1

    # Get section HTML
    html = sectionResponse.read()

    # Be    gin parsing read HTML
    soup = BeautifulSoup(html)

    # Get number total of pages!
    pageshref = '^/f\d+p\d+-.*$'
    pages = soup.findAll('a', attrs={'href':re.compile(pageshref)})

    if len(pages):
        # Will use the previous to last element as last element will have no value (it's a "next" link)
        totalpages = int(pages[len(pages)-2].string) # Last element of the list!

    print "Página totales en la seccion: %(total)d" % {'total':totalpages}
    
    # First of all, retrieve the messages from page 1
    msghref = '^/t\d+-\w+.*$'
    # Find the divs containing the messages
    for link in soup.findAll('a', attrs={'class':'topictitle',
                                         'href':re.compile(msghref)}):
        print "Añadiendo mensaje ",link.string, "con url", link['href']
        messages.append((idx,link.string,link['href'],1))

    
    # Retrieve rest of messages from pages.
    if totalpages > 1:
        # Prepare URL /f<Number>p<50*page>-<restURL>
        pos = url.find('-')
        assert pos > 0
        leftUrl = url[:pos]
        rightUrl = url[pos:]
        # Begin in 2, we have parsed page # 1
        for page in range(2, totalpages):
            pageUrl = '%(base)s%(left)sp%(pagen)d%(right)s' % \
                      {'base':globals.URL,
                       'left':leftUrl,
                       'pagen':(page-1)*50,
                       'right':rightUrl}
            response = browser.open(pageUrl)
            html = response.read()
            getMessagesInPage(html, idx, messages, page)

# Main method with all the functionality
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

    # Get administration TID (and assert value is valid!)
    tid = getAdminTid(html)
    print tid
#    assert tid != ''

    # Get main sections from given html
    sections = getSections(html)
    # sort sections
    sections.sort
    
    # Traverse the list of sections and retrieve the list of messages
    for idx, name, url in sections:
        print "Cargando mensajes de la sección ", name
        getMessagesInSection(browser, idx, url)
        


if __name__ == '__main__':

    if len(sys.argv) < 2:
        section = 'clubsuperblackbird'
    else:
        section = sys.argv[1]
    backup(section)
