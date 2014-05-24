#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-05-18 13:06:23 vk>

## TODO:
## * fix parts marked with «FIXXME»

import os
import re
from sys import stdin, exit, argv, exit
import codecs
import time
from subprocess import call
from shutil import move

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2014-05-18"


EPILOG = u"\n\
  :copyright:  (c) 2015 and following by Karl Voit <tools@Karl-Voit.at>\n\
  :license:    GPL v3 or any later version\n\
  :URL:       \n\
  :bugreports: via github (preferred) or <tools@Karl-Voit.at>\n\
  :version:    " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"

## OLD: set editor="vim -c 'set tw=68 et' '+/^$'"
## NEW: set editor="/home/karl/bin/python /home/karl/bin/vkmuttfilter.py"
## NEW: set editor="/usr/bin/python /home/vk/src/muttfilter.py/muttfilter.py"

HOME = os.path.expanduser("~")

TMPFILENAME = HOME + "/tmp/mutt-vkmuttfilter-tempfile-which-can-be-deleted.txt"
LOGFILENAME = HOME + "/tmp/mutt-vkmuttfilter.log"
ORGCONTACTSFILE = HOME + "/org/contacts.org"

ORGCONTACTS_PROPERTY_RECIPIENT_ADDRESS = ":EMAIL:"
ORGCONTACTS_PROPERTY_MYNEWFROMADDRESS = ":ITOLDTHEM_EMAIL:"
DEFAULT_EMAIL_ADDRESS = "mail@Karl-Voit.at"

## please configure vimrc for filetype mail accordingly:
EDITOR = os.environ.get('EDITOR','vim')

## FIXXME: editor parameters (go to first line after the first empty one) are not working:
EDITORPARAMS = "+'/^$/+1'"
EDITORPARAMS = '+\'/^\$/+1\''

## FIXXME: fix RegEx to match FIRST email address; for now, it gets last one!
FIRSTEMAILADDRESS=re.compile(u'(.*[< ])?(.+)@([^> ]+)([> ].*)?', flags = re.U)

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
                address = extractFirstEmailaddress(inputline).strip()
                if address:
                    log.write('found email address: [%s]\n' % (address))
                    header['from'] = address
                else:
                    log.write('WARNING: found \"From: \" but failed to parse email address!\n')
            elif inputline.startswith('To: '):
                log.write('found \"To: \"; trying to parse email address ...\n')
                address = extractFirstEmailaddress(inputline).strip()
                if address:
                    log.write('found email address: [%s]\n' % (address))
                    header['to'] = extractFirstEmailaddress(inputline)
                else:
                    log.write('WARNING: found \"To: \" but failed to parse email address!\n')

    log.write('WARNING: should never be reached (parseEmailHeader)\n')
    return None

                    
def parseOrgContactsProperties(log, orgcontactsfile):

    SEARCHING_PROPERTY_DRAWER = 0
    IN_PROPERTY_DRAWER = 1
    state = SEARCHING_PROPERTY_DRAWER

    contact_properties = []  ## consists of list of current_contacts as below
    current_contact = [[], None]  ## consists of list of RECIPIENT_ADDRESSES and one MYNEWFROMADDRESS

    number_of_property_drawers = 0
    number_of_mynewfromaddress = 0
    
    for line in codecs.open(orgcontactsfile, 'r', encoding='utf-8'):
        
        if state==SEARCHING_PROPERTY_DRAWER:
            if line.upper().startswith(':PROPERTIES:'):
                number_of_property_drawers+=1
                state=IN_PROPERTY_DRAWER
                current_contact = [[], None]
            else:
                continue
            
        elif state==IN_PROPERTY_DRAWER:
            if line.upper().startswith(':END:'):
                state=SEARCHING_PROPERTY_DRAWER
                if current_contact[1]:
                    ## found MYNEWFROMADDRESS
                    if len(current_contact[0]) > 0:
                        ## both contain content: MYNEWFROMADDRESS and RECIPIENT_ADDRESS
                        contact_properties.append(current_contact)
                        log.write(str(current_contact) + '\n')
                continue
            else:
                if line.upper().startswith(ORGCONTACTS_PROPERTY_MYNEWFROMADDRESS):
                    emailaddress = extractFirstEmailaddress(line)
                    if emailaddress:
                        number_of_mynewfromaddress+=1
                        current_contact[1] = emailaddress.strip()
                elif line.upper().startswith(ORGCONTACTS_PROPERTY_RECIPIENT_ADDRESS):
                    emailaddress = extractFirstEmailaddress(line)
                    if emailaddress:
                        current_contact[0].append(emailaddress.strip())

    log.write('Found ' + str(number_of_property_drawers) + ' property drawers with ' + \
              str(number_of_mynewfromaddress) + ' mynewfromaddresses\n')
    return contact_properties


def rewriteEmail(log, muttfilename, tempfilename, itoldthem_email):
    
    log.write('re-writing email ...\n')
    with codecs.open(tempfilename, 'wb', encoding='utf-8') as output:
        for inputline in codecs.open(muttfilename, 'r', encoding='utf-8'):
                if inputline.startswith("From: "):
                        output.write('From: ' + itoldthem_email + '\n')
                        output.write(u'X-muttfilter: changed From-address to: ' + itoldthem_email + '\n')
                else:
                    ## write unmodified
                    output.write(inputline)
    
    log.write('re-wrote email\n')

    

def replaceFileWithOther(log, filetooverwrite, replacement):
    
    assert(os.path.isfile(filetooverwrite))
    assert(os.path.isfile(replacement))

    os.remove(filetooverwrite)
    log.write('removed filetooverwrite [%s]\nrenaming replacement [%s] to filetooverwrite ...\n' % (filetooverwrite, replacement))
    try:
        #os.rename(replacement, filetooverwrite)  ## "[Errno 18] Invalid cross-device link"
        #os.system('mv "%s" "%s"' % (replacement, filetooverwrite))  ## *dirty* workaround! replaced by:
        src_basename = os.path.basename(replacement)
        dst_basename = os.path.basename(filetooverwrite)
        src_dirname = os.path.dirname(replacement)
        dst_dirname = os.path.dirname(filetooverwrite)
        os.rename(replacement, os.path.join(src_dirname, dst_basename))
        move(os.path.join(src_dirname, dst_basename), dst_dirname)
    except Exception, e:
        log.write("Rename failed: %s\n" % e)
    log.write('renamed replacement to filetooverwrite\n')

    assert(os.path.isfile(filetooverwrite))
    assert(os.path.isfile(replacement) == False)

    
def orgContactPropertiesLookup(log, contact_properties, to):
    """
    Skims through the parsed OrgContacts properties and searches for
    "to" and returns corresponding "ORGCONTACTS_PROPERTY_MYNEWFROMADDRESS" if found. None if not.
    """

    for contact in contact_properties:
        for address in contact[0]:
            if to.lower() == address.lower():
                return contact[1]

    return None


if __name__ == "__main__":

    mydescription = u"Modifying recipient email address in mutt emails if orgcontacts \n" + \
                    "has a different from-address associated. Please refer to \n" + \
                    "https://github.com/novoid/muttfilter.py for more information."

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

            ## parsing contacts.org to get pairs of
            ## ORGCONTACTS_PROPERTY_RECIPIENT_ADDRESS and
            ## ORGCONTACTS_PROPERTY_MYNEWFROMADDRESS
            contact_properties = parseOrgContactsProperties(log, ORGCONTACTSFILE)
            log.write('found ' + str(len(contact_properties)) + \
                      ' contacts with RECIPIENT_ADDRESS(ES) and MYNEWFROMADDRESS\n')

            log.write('looking for recipient \"%s\" within contact data...\n' % (emailheadercomponents['to'].strip()))
            itoldthem_email = orgContactPropertiesLookup(log, contact_properties, emailheadercomponents['to'].strip())
            if itoldthem_email:
                log.write('found matching RECIPIENT_ADDRESS and MYNEWFROMADDRESS; checking current From (if it is unmodified) ...\n')
                if emailheadercomponents['from'].lower() == DEFAULT_EMAIL_ADDRESS.lower():
                    log.write('Yes, I *re-write/modify the email* ...   (with tmpfile [%s] and muttfilename[%s])\n' % \
                              (TMPFILENAME, muttfilename))
                    rewriteEmail(log, muttfilename, TMPFILENAME, itoldthem_email)
                    log.write('re-wrote email, replacing original file with new one ...\n')
                    replaceFileWithOther(log, muttfilename, TMPFILENAME)
                else:
                    log.write('found modified From [%s]; *not* re-writing email\n' % (emailheadercomponents['from']))
            else:
                log.write('found no matching RECIPIENT_ADDRESS and MYNEWFROMADDRESS; *not* re-writing email\n')
                
            log.write('calling EDITOR ...\n')
            #call([EDITOR, EDITORPARAMS, muttfilename])
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
