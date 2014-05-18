#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-05-18 11:35:26 vk>

## TODO:
## * rename to vkmuttfilter
## * fix parts marked with «FIXXME»

import os
import re
from sys import stdin, exit, argv, exit
import codecs
import time
from subprocess import call

## debugging:   for setting a breakpoint:
#pdb.set_trace()## FIXXME
import pdb

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2014-05-15"


EPILOG = u"\n\
  :copyright:  (c) 2015 and following by Karl Voit <tools@Karl-Voit.at>\n\
  :license:    GPL v3 or any later version\n\
  :URL:       \n\
  :bugreports: via github (preferred) or <tools@Karl-Voit.at>\n\
  :version:    " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"

## OLD: set editor="vim -c 'set tw=68 et' '+/^$'"
## NEW: set editor="/home/karl/bin/python /home/karl/bin/vkmuttfilter.py"

HOME = os.path.expanduser("~")

TMPFILENAME = HOME + "/tmp/mutt-vkmuttfilter-tempfile-which-can-be-deleted.txt"
LOGFILENAME = HOME + "/tmp/mutt-vkmuttfilter.log"
ORGCONTACTSFILE = HOME + "/org/contacts.org"


## please configure vimrc for filetype mail accordingly:
EDITOR = os.environ.get('EDITOR','vim')

FIRSTEMAILADDRESS=re.compile(u'(.*[< ])?(.+)@(.+)([> ].*)?', flags = re.U)

def error_exit(muttemailfilename, errorcode, message):
    """
    Quits program (not deleting logfile).
    """

    log.write('ERROR ' + str(errorcode) + ': ' + message + '\n')
    
    ## replacing tmpfile with log:
    log.flush()
    replaceFileWithOther(log, muttemailfilename, LOGFILENAME)

    exit(errorcode)

def extractFirstEmailaddress(inputline):
    """
    Parses a string and extracts the first email address found.
    """
    components = FIRSTEMAILADDRESS.match(inputline)
    if not components:
        ## no email address found
        return None
    else:
        if len(components.group(2)) > 0 and len(components.group(3)) > 0:
            return components.group(2) + "@" + components.group(3)
        else:
            ## not all email components found:
            return None

def parseEmailHeader(log, emailfile):
    """
    Parses the header of a file containing an email and returns From and To accordingly.
    """

    header = {}

    for inputline in codecs.open(emailfile, 'r', encoding='utf-8'):
            if inputline == '\n':
                if 'from' in header.keys() and 'to' in header.keys():
                    log.write('found \"from\" and \"to\" in header\n')
                    return header
                else:
                    return None
            elif inputline.startswith('From: '):
                log.write('found \"From: \"; trying to parse email address ...\n')
                address = extractFirstEmailaddress(inputline)
                if address:
                    log.write('found email address\n')
                    header['from'] = address
                else:
                    log.write('WARNING: found \"From: \" but failed to parse email address!\n')
            elif inputline.startswith('To: '):
                log.write('found \"To: \"; trying to parse email address ...\n')
                address = extractFirstEmailaddress(inputline)
                if address:
                    log.write('found email address\n')
                    header['to'] = extractFirstEmailaddress(inputline)
                else:
                    log.write('WARNING: found \"To: \" but failed to parse email address!\n')

    log.write('WARNING: should never be reached (parseEmailHeader)\n')
    return None

                    
def parseOrgContactsProperties(log, orgcontactsfile):

    
    pass ## FIXXME: implement


def rewriteEmail(log, muttfilename, tempfilename):
    
    log.write('re-writing email ...\n')
    with codecs.open(tempfilename, 'wb', encoding='utf-8') as output:
        for inputline in codecs.open(muttfilename, 'r', encoding='utf-8'):
                if inputline.startswith("Subject: "):
                        ## for testing purposes, just re-write subject line
                        output.write(inputline.strip() + u" added by vkmuttfilter!" + '\n')
                        output.write(u'X-muttfilter: modified subject line because FIXXME\n')
                else:
                    ## write unmodified
                    output.write(inputline)
    
    log.write('re-wrote email\n')

    replaceFileWithOther(log, filetooverwrite, newfile, deleteold=False)
    
    assert(os.path.isfile(muttfilename))
    assert(os.path.isfile(tempfilename))

    os.remove(muttfilename)
    log.write('removed muttfilename; renaming tempfilename to muttfilename ...\n')
    try:
        #os.rename(tempfilename, muttfilename)  ## "[Errno 18] Invalid cross-device link"
        ## FIXXME: replace mv-command with Python-move-method of any kind in order to stay OS-independent:
        os.system('mv "%s" "%s"' % (tempfilename, muttfilename))
    except Exception, e:
        log.write("Rename failed: %s\n" % e)
    log.write('renamed tempfilename to muttfilename\n')

    assert(os.path.isfile(muttfilename))
    assert(os.path.isfile(tempfilename) == False)
    #log.write('after asserting new situation; updating utime ...\n')

    #time.sleep(1)

    ## manually updating mtime:
    #os.utime(muttfilename, None)

def replaceFileWithOther(log, filetooverwrite, newfile):
    
    assert(os.path.isfile(filetooverwrite))
    assert(os.path.isfile(newfile))

    os.remove(filetooverwrite)
    log.write('removed filetooverwrite; renaming newfile to filetooverwrite ...\n')
    try:
        #os.rename(newfile, filetooverwrite)  ## "[Errno 18] Invalid cross-device link"
        ## FIXXME: replace mv-command with Python-move-method of any kind in order to stay OS-independent:
        os.system('mv "%s" "%s"' % (newfile, filetooverwrite))
    except Exception, e:
        log.write("Rename failed: %s\n" % e)
    log.write('renamed newfile to filetooverwrite\n')

    assert(os.path.isfile(filetooverwrite))
    assert(os.path.isfile(newfile) == False)
    #log.write('after asserting new situation; updating utime ...\n')

    
def orgContactPropertiesLookup(log, contact_properties, to):
    """
    Skims through the parsed OrgContacts properties and searches for
    "to" and returns corresponding "ITOLDTHEM_EMAIL" if found. None if not.
    """

    pass ## FIXXME: implement


if __name__ == "__main__":

    mydescription = u"FIXXME: Please refer to \n" + \
        "https://github.com/novoid/FIXXME for more information."

    with codecs.open(LOGFILENAME, 'wb', encoding='utf-8') as log:

        log.write('=========================\nscript called\n')
        try:
           
            muttfilename = argv[1]
            if not os.path.isfile(muttfilename):
                print "ERROR: no file found as parameter 1"
                log.write('ERROR: no file found as parameter 1\n')
    
            log.write('EDITOR[%s] muttfilename[%s] TMPFILENAME[%s]\n' % (EDITOR, muttfilename, TMPFILENAME))

            ## parsing header only to get From and To
            emailheadercomponents = parseEmailHeader(log, muttfilename)
            if not emailheadercomponents:
                error_exit(muttfilename, 10, 'ERROR: could not parse \"from\" and/or \"to\" from email header! :-O\n')

            ## FIXXME: parsing contacts.org to get pairs of EMAIL and ITOLDTHEM
            contact_properties = parseOrgContactsProperties(log, ORGCONTACTSFILE)
   
            itoldthem_email = orgContactPropertiesLookup(log, contact_properties, emailheadercomponents['to'])
            if emailheadercomponents['from'] == 'mail@karl-voit.at' and itoldthem_email:
                log.write('I recognized that I should re-write the email ...\n')
                rewriteEmail(log, muttfilename, TMPFILENAME)
                log.write('re-wrote email, replacing original file with new one ...\n')
                replaceFileWithOther(log, muttfilename, TMPFILENAME)
                
            log.write('calling EDITOR ...\n')
            call([EDITOR, muttfilename])
            log.write('after EDITOR\n')

            log.write('end.\n')


        except KeyboardInterrupt:
    
            pass

        os.remove(LOGFILENAME) ## delete it if no error happened!

## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
