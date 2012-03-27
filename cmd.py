#!/usr/bin/env python
import sys
if sys.version_info < (2, 4):
    print "Your python interpreter is too old. Please consider upgrading."
    sys.exit(1)

if sys.version_info < (2, 5):
    import site
    import os.path
    from distutils.sysconfig import get_python_lib
    found = False
    module_dir = get_python_lib()
    for name in os.listdir(module_dir):
        lowername = name.lower()
        if lowername[0:10] == 'sqlalchemy' and 'egg' in lowername:
            sqlalchemy_dir = os.path.join(module_dir, name)
            if os.path.isdir(sqlalchemy_dir):
                site.addsitedir(sqlalchemy_dir)
                found = True
                break
    if not found:
        print "Could not find SQLAlchemy installed."
        sys.exit(1)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import dishpub.dishpubdb as model
import os.path
import logging
import optparse
from dishpub.__version__ import version
import dishpub
import urllib2
import urllib
import hashlib
import datetime
import os, statvfs
import shutil
import commands
try:
    import simplejson as json
except:
    import json

import urlparse
import subprocess
import time


def main():
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logfile', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Logfile configuration file.', metavar='CFG_FILE')
    p.add_option('--imagelist-list', action ='store_true',help='write to stdout the list images.', metavar='IMAGE_UUID')
    p.add_option('--imagelist-add', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    p.add_option('--imagelist-del', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    
    p.add_option('--imagelist-upload', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    
    p.add_option('--imagelist-show', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    # Key value pairs to add to an image
    p.add_option('--imagelist-keys', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-key', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-value', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    
    p.add_option('--image', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-add', action ='store',help='Add image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-del', action ='store',help='Add image UUID.', metavar='CFG_LOGFILE')

    # Key value pairs to add to an image
    
    p.add_option('--image-keys', action ='store_true',help='Show keys for image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-key', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-value', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-upload', action ='store',help='Path to image UUID.', metavar='CFG_LOGFILE')
    
    
    
    
    
    
    options, arguments = p.parse_args()
    
    # Set up basic variables
    logFile = None
    databaseConnectionString = None
    
    # Read enviroment variables
    if 'DISH_LOG_CONF' in os.environ:
        logFile = os.environ['VMILS_LOG_CONF']
    if 'DISH_RDBMS' in os.environ:
        databaseConnectionString = os.environ['VMILS_RDBMS']
    
    
    # Set up log file
    if options.logfile:
        logFile = options.logfile
    if logFile != None:
        if os.path.isfile(str(options.logfile)):
            logging.config.fileConfig(options.logfile)
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.logfile))
            sys.exit(1)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")
    
    # Now process command line
    
    if options.database:
        databaseConnectionString = options.database
    
    print dir(options)
    
    # Now default unset values
    
    if databaseConnectionString == None:
        databaseConnectionString = 'sqlite:///dish.db'
        log.info("Defaulting DB connection to '%s'" % (databaseConnectionString))
    
    engine = create_engine(databaseConnectionString, echo=False)
    model.init(engine)
    SessionFactory = sessionmaker(bind=engine)
    Session = SessionFactory()
    
if __name__ == "__main__":
    main()
