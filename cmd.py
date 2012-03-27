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


class imagelistpub:
    def __init__(self,databaseConnectionString):
        self.log = logging.getLogger("imagelistpub")
        self.engine = create_engine(databaseConnectionString, echo=False)
        model.init(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        #self.Session = self.SessionFactory()
    def imagesList(self):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Subscription)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')            
        for imagelist in query_imagelists:
            print imagelist.identifier
        
    def imagesAdd(self,UUID):
        Session = self.SessionFactory()
        details = { u'dc:identifier' : str(UUID),
            u'dc:description' : str(UUID),
            u'hv:uri' : str(UUID),
        }
        newImage = model.Subscription(details,True)
        Session.add(newImage)
        Session.commit()
        return True

    def imagesDel(self,UUID):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Subscription).\
                filter(model.Subscription.identifier == UUID )
        for item in query_imagelists:
            Session.delete(item)
        Session.commit()
        return True




    def imagesShow(self,UUID):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Subscription).\
                filter(model.Subscription.identifier == UUID )
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        imagelist = query_imagelists.one()
        outModel = {
                u'dc:identifier' : imagelist.identifier
            }
        return json.dumps(outModel,sort_keys=True, indent=2)
        
    def imagelist_key_update(self,imageListUuid, imagelist_key, imagelist_key_value):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Subscription).\
                filter(model.Subscription.identifier == imageListUuid)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        query_imagekeys = Session.query(model.Subscription).\
                filter(model.Subscription.identifier == imageListUuid)
        print query_imagelists.one()
        
def main():
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logfile', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Logfile configuration file.', metavar='CFG_FILE')
    p.add_option('--imagelist', action ='store',help='select imagelist.', metavar='IMAGELIST_UUID')
    p.add_option('--imagelist-list', action ='store_true',help='write to stdout the list images.')
    p.add_option('--imagelist-add', action ='store_true',help='write to stdout the image list.')
    p.add_option('--imagelist-del', action ='store_true',help='write to stdout the image list.')
    
    p.add_option('--imagelist-show', action ='store_true',help='write to stdout the list images.', metavar='IMAGE_UUID')
    p.add_option('--imagelist-upload', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    
    # Key value pairs to add to an image
    p.add_option('--imagelist-keys', action ='store_true',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-key-add', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-key-del', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
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
    imagelistUUID = None
    imagelist_req = False
    imagelist_key = None
    imagelist_key_add_req = False
    imagelist_key_value = None
    imagelist_key_value_add_req = False

    
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
    actions = set([])
    if options.imagelist:
        imagelistUUID = options.imagelist
    if options.imagelist_list:
        actions.add('imagelist_list')
        
    if options.imagelist_add:
        actions.add('imagelist_add')
        imagelist_req = True
        
    if options.imagelist_show:
        actions.add('imagelist_show')
        imagelist_req = True
        
    if options.imagelist_del:
        actions.add('imagelist_del')
        imagelist_req = True
        
    if options.imagelist_keys:
        actions.add('imagelist_keys')
        imagelist_req = True
        
    if options.imagelist_key_add:
        actions.add('imagelist_key_update')
        imagelist_req = True
        imagelist_key_value_add_req = True
        imagelist_key = options.imagelist_key_add
        
    if options.imagelist_value:
        actions.add('imagelist_key_update')
        imagelist_req = True
        imagelist_key_add_req = True
        imagelist_key_value = options.imagelist_value
    
    if options.database:
        databaseConnectionString = options.database
    
    actionsLen = len(actions)
    if actionsLen == 0:
        log.error('No actions added')
        sys.exit(1)
    if actionsLen > 1:
        log.error('To many actions added')
        sys.exit(1)
    
    
    # Now default unset values
    
    if databaseConnectionString == None:
        databaseConnectionString = 'sqlite:///dish.db'
        log.info("Defaulting DB connection to '%s'" % (databaseConnectionString))
    
    # Now check for required fields
    
    if imagelist_req:
        if imagelistUUID == None:
            log.error('Image list UUID is needed')
            sys.exit(1)
    
    # now do the work.
    
    imagepub = imagelistpub(databaseConnectionString)
    
    if 'imagelist_list' in actions:
        imagepub.imagesList()
    if 'imagelist_show' in actions:
        output = imagepub.imagesShow(imagelistUUID)
        if output != None:
            print output
    
    if 'imagelist_add' in actions:
        imagepub.imagesAdd(imagelistUUID)
    
    if 'imagelist_del' in actions:
        imagepub.imagesDel(imagelistUUID)
    if 'imagelist_key_update' in actions:
        #imagepub.imagesDel(imagelistUUID)
        imagepub.imagelist_key_update(imagelistUUID, imagelist_key, imagelist_key_value)
    
    
    
    
    
if __name__ == "__main__":
    main()
