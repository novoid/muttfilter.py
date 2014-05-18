#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-04-20 21:57:35 vk>

## TODO:
## * rename to vkmuttfilter
## * fix parts marked with «FIXXME»

import os
from sys import stdin, exit, argv
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

TMPFILENAME = "/home/karl/tmp/mutt-vkmuttfilter-tempfile-which-can-be-deleted.txt"
LOGFILENAME = "/home/karl/tmp/mutt-vkmuttfilter.log"

ORGCONTACTSFILE = "/home/karl/org/contacts.org"

## please configure vimrc for filetype mail accordingly:
EDITOR = os.environ.get('EDITOR','vim')

def parseEmailHeader(log, emailfile):
    """
    Parses the header of a file containing an email and returns From and To accordingly.
    """

    header = None

    for inputline in codecs.open(emailfile, 'r', encoding='utf-8'):
            if len(inputline) <1:
                    return header
            elif inputline.startswith('From: '):
                    header{'from'} = extractFirstEmailaddress(inputline)
            elif inputline.startswith('To: '):
                    header{'to'} = extractFirstEmailaddress(inputline)

def parseOrgContacts(log, orgcontactsfile):
    pass

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
    
            log.write('EDITOR[%s] muttfilename[%s] TMPFILENAME[%s]' % (EDITOR, muttfilename, TMPFILENAME))

            ## FIXXME: parsing header only to get From and To
            muttheader = parseEmailHeader(log, muttfilename)
            ## FIXXME: parsing contacts.org to get pairs of EMAIL and ITOLDTHEM
            contacts = parseOrgContacts(log, ORGCONTACTSFILE)
   
            ## algorithm:
            ## if From == mail@karl-voit.at
            ## and To found in contacts.org (as :EMAIL:)
            ## and corresponding ITOLDTHEM is set
            ## then re-write email

            ## re-write email:
            log.write('re-writing email ...\n')
            with codecs.open(TMPFILENAME, 'wb', encoding='utf-8') as output:
                for inputline in codecs.open(muttfilename, 'r', encoding='utf-8'):
                        if inputline.startswith("Subject: "):
                                ## for testing purposes, just re-write subject line
                                output.write(inputline.strip() + u" added by vkmuttfilter!" + '\n')
                                output.write(u'X-muttfilter: modified subject line because FIXXME\n')
                        else:
                            ## write unmodified
                            output.write(inputline)
    
            log.write('re-wrote email\n')

            assert(os.path.isfile(muttfilename))
            assert(os.path.isfile(TMPFILENAME))

            os.remove(muttfilename)
            log.write('removed muttfilename; renaming TMPFILENAME to muttfilename ...\n')
            try:
                #os.rename(TMPFILENAME, muttfilename)  ## "[Errno 18] Invalid cross-device link"
                ## FIXXME: replace mv-command with Python-move-method of any kind in order to stay OS-independent:
                os.system('mv "%s" "%s"' % (TMPFILENAME, muttfilename))
            except Exception, e:
                log.write("Rename failed: %s\n" % e)
            log.write('renamed TMPFILENAME to muttfilename\n')

            assert(os.path.isfile(muttfilename))
            assert(os.path.isfile(TMPFILENAME) == False)
            log.write('after asserting new situation; updating utime ...\n')

            time.sleep(1)

            ## manually updating mtime:
            os.utime(muttfilename, None)

            log.write('calling EDITOR ...\n')
            call([EDITOR, muttfilename])
            log.write('after EDITOR\n')

            time.sleep(1)
    
            log.write('end.\n')


        except KeyboardInterrupt:
    
            pass

        os.remove(LOGFILENAME) ## delete it if no error happened!

## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
