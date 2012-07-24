#!/usr/bin/env python
import sys

import dishpub.dishpubdb as model
import dishpub.state as dishpubstate
import dishpub.uploader as uploader


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
import types
# needed for the signing of images.
import M2Crypto.SMIME
import M2Crypto.BIO

def checkVoms(requiredExtensions = set([])):
    log = logging.getLogger("vomscheck")
    cmd = "voms-proxy-info  --all"
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processRc = None
    handleprocess = True
    counter = 0
    stdout = ''
    stderr = ''
    while handleprocess:
        counter += 1
        time.sleep(1)
        cout,cerr = process.communicate()
        stdout += cout
        stderr += cerr
        process.poll()
        processRc = process.returncode
        if processRc != None:
            break
        if counter == timeout:
            os.kill(process.pid, signal.SIGQUIT)
        if counter > timeout:
            os.kill(process.pid, signal.SIGKILL)
            processRc = -9
            break
    
    if processRc != 0:
        log.error("Failed to run voms-proxy-info sucessfully")
        log.info("stdout:%s" % (stdout))
        log.info("stderr:%s" % (stderr))
        return None
    vomsInfo = {}
    foundVos = set([])
    issuer = None
    identity = None
    for lineUnclean in stdout.split('\n'):
        foundPos = lineUnclean.find(':')
        if foundPos > 0:
            head = lineUnclean[:foundPos].strip(' \t\n\r')
            tail = lineUnclean[(foundPos +1):].strip(' \t\n\r')
            if head == 'timeleft':
                if tail == '0:00:00':
                    log.error("Proxy expired.")
                    return None
            if head == 'VO':
                foundVos.add(tail)
            if head == 'identity':
                identity = tail
    if len(requiredExtensions.difference(foundVos)) > 0:
        log.error("not all extensions found")
        return None
    return identity


def main():
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-d', '--database', action ='store', help='Database conection string')
    p.add_option('-L', '--logfile', action ='store',help='Logfile configuration file.', metavar='CFG_LOGFILE')
    p.add_option('-C', '--config-file', action ='store',help='Configuration file.', metavar='CFG_FILE')
    
    p.add_option('--endorser', action ='store',help='select endorser.', metavar='ENDORSER')
    p.add_option('--endorser-show', action ='store_true',help='write to stdout the endorser.')
    p.add_option('--endorser-list', action ='store_true',help='write to stdout the endorsers list.')
    p.add_option('--endorser-add', action ='store',help='Endorser create.')
    p.add_option('--endorser-del', action ='store',help='Endorser delete .')
    
    p.add_option('--endorser-key-update', action ='store',help='Endorser metadata key to create/overwrite.')
    p.add_option('--endorser-key-del', action ='store_true',help='Endorser metadata key to delete.')
    p.add_option('--endorser-value', action ='store',help='write to stdout the image list.')
    
    p.add_option('--connect', action ='store_true',help='Bind Endorser to imagelist.')
    p.add_option('--disconnect', action ='store_true',help='Unbind Endorser to imagelist.')
    
    p.add_option('--imagelist', action ='store',help='select imagelist.', metavar='IMAGELIST_UUID')
    p.add_option('--imagelist-list', action ='store_true',help='write to stdout the list images.')
    p.add_option('--imagelist-add', action ='store_true',help='write to stdout the image list.')
    p.add_option('--imagelist-del', action ='store_true',help='write to stdout the image list.')
    
    p.add_option('--imagelist-show', action ='store_true',help='write to stdout the list images.', metavar='IMAGE_UUID')
    p.add_option('--imagelist-upload', action ='store_true',help='write to stdout the image list.', metavar='IMAGE_UUID')
    p.add_option('--imagelist-import-smime', action ='store',help='Import an image list.', metavar='IMAGE_PATH')
    p.add_option('--imagelist-import-json', action ='store',help='Import an image list.', metavar='IMAGE_PATH')
    
    # Key value pairs to add to an image
    p.add_option('--imagelist-keys', action ='store_true',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-key-add', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-key-del', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    p.add_option('--imagelist-value', action ='store',help='Edit imagelist.', metavar='CFG_LOGFILE')
    
    p.add_option('--image-list', action ='store_true',help='Edit image UUID.', metavar='CFG_LOGFILE')    
    p.add_option('--image', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-add', action ='store',help='Add image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-del', action ='store',help='Add image UUID.', metavar='CFG_LOGFILE')

    # Key value pairs to add to an image
    
    p.add_option('--image-keys', action ='store_true',help='Show keys for image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-key-add', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
    p.add_option('--image-key-del', action ='store',help='Edit image UUID.', metavar='CFG_LOGFILE')
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
    imagelist_import_json = None
    imageUuid = None
    image_key = None
    image_key_req = False
    image_req = None
    image_key_value = None
    image_key_value_add_req = False
    endorserSub = None
    endorser_req  = False
    endorserKey = None
    endorserKeyReq = False
    
    endorserValue = None
    endorserValueReq = False
    
    imageFileLocal = None
    
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
    
    

    if options.endorser:
        endorserSub = options.endorser

    if options.endorser_list:
        actions.add('endorser_list')
        
    if options.endorser_show:
        actions.add('endorser_show')
        endorser_req = True
        
    if options.endorser_add:
        actions.add('endorser_add')
        endorserSub = options.endorser_add

    if options.endorser_del:
        actions.add('endorser_del')
        endorserSub = options.endorser_del

    if options.endorser_key_update:
        actions.add('endorser_key_update')
        endorserKey = options.endorser_key_update
        
    if options.endorser_key_del:
        actions.add('endorser_key_del')
        endorser_req = True

    if options.endorser_value:
        endorserValue = options.endorser_value
        endorser_req = True
    if options.connect:
        endorser_req = True
        imagelist_req = True
        actions.add('connect')
    if options.disconnect:
        endorser_req = True
        imagelist_req = True
        actions.add('disconnect')
    
    if options.imagelist:
        imagelistUUID = options.imagelist
    if options.imagelist_list:
        actions.add('imagelist_list')
        
    if options.imagelist_add:
        actions.add('imagelist_add')
        imagelist_req = True

    if options.imagelist_del:
        actions.add('imagelist_del')
        imagelist_req = True
    
    if options.imagelist_show:
        actions.add('imagelist_show')
        imagelist_req = True
        
    if options.imagelist_keys:
        actions.add('imagelist_keys')
        imagelist_req = True
        
    if options.imagelist_key_add:
        actions.add('imagelist_key_update')
        imagelist_req = True
        imagelist_key_value_add_req = True
        imagelist_key = options.imagelist_key_add
    if options.imagelist_key_del:
        actions.add('imagelist_key_del')
        imagelist_req = True
        imagelist_key = options.imagelist_key_del
      
    if options.imagelist_value:
        actions.add('imagelist_key_update')
        imagelist_req = True
        imagelist_key_add_req = True
        imagelist_key_value = options.imagelist_value
    
    if options.imagelist_import_smime:
        actions.add('imagelist_import_smime')
        
        imagelist_import_smime = options.imagelist_import_smime
    if options.imagelist_import_json:
        actions.add('imagelist_import_json')
        
        imagelist_import_json = options.imagelist_import_json
    if options.image_list:
        actions.add('image_list')
    if options.image:
        imageUuid = options.image
    
    if options.image_add:
        actions.add('image_add')
        image_req = True
        image_key = options.image_add
    
    if options.image_keys:
        actions.add('image_keys')
        imagelist_req = True
        image_req = True

    if options.image_key_add:
        actions.add('image_key_update')
        image_req = True
        image_key_value_add_req = True
        image_key = options.image_key_add

    if options.image_value:
        actions.add('image_key_update')
        image_req = True
        image_key_req = True
        image_key_value = options.image_value
    if options.image_upload:
        actions.add('image_upload')
        imageFileLocal = options.image_upload
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
    if image_req:
        if imageUuid == None:
            log.error('Image UUID is needed')
            sys.exit(1)
    if endorser_req:
        if endorserSub == None:
            log.error('Endorser subject is needed')
            sys.exit(1)
    # now do the work.
    
    imagepub = dishpubstate.imagelistpub(databaseConnectionString)
    
    if 'endorser_list' in actions:
        imagepub.endorserList()
    if 'endorser_show' in actions:
        print imagepub.endorserDump(endorserSub)
    
    if 'endorser_add' in actions:
        imagepub.endorserAdd(endorserSub)
    if 'endorser_del' in actions:
        imagepub.endorserDel(endorserSub)
    if 'endorser_key_update' in actions:
        imagepub.endorserMetadataUpdate(endorserSub,endorserKey,endorserValue)
    if 'endorser_key_del' in actions:
        imagepub.endorserMetadataDel(endorserSub,endorserKey)
    
    if 'connect' in actions:
        imagepub.imageListEndorserConnect(imagelistUUID,endorserSub)

    if 'disconnect' in actions:
        imagepub.imageListEndorserDisconnect(imagelistUUID,endorserSub)
    
    if 'imagelist_list' in actions:
        imagepub.imageListList()
    if 'imagelist_show' in actions:
        output = json.dumps(imagepub.imagesShow(imagelistUUID),sort_keys=True, indent=4)
        if output != None:
            print output
    
    if 'imagelist_add' in actions:
        imagepub.imageListAdd(imagelistUUID)
    
    if 'imagelist_del' in actions:
        imagepub.imagesDel(imagelistUUID)
    if 'imagelist_key_update' in actions:
        imagepub.imagelist_key_update(imagelistUUID, imagelist_key, imagelist_key_value)
    if 'imagelist_key_del' in actions:
        imagepub.imagelist_key_del(imagelistUUID, imagelist_key)
    
    if 'imagelist_import_smime' in actions:
        
        
        fp = open (imagelist_import_smime)
        inportText = fp.read()
        buf = M2Crypto.BIO.MemoryBuffer(str(inportText))
        try:
            p7, data = M2Crypto.SMIME.smime_load_pkcs7_bio(buf)
        except AttributeError, e:
            log.error("Failed to load SMIME")
            raise e
        readData = data.read()
        try:
            candidate = json.loads(str(readData))
        except ValueError:
            log.error("Failed to parse JSON.")
            sys.exit(20)
            
        if candidate == None:
            log.error("No JSON content.")
            sys.exit(21)
        
        imagepub.importer(candidate)
        
        
        
    if 'image_list' in actions:
        images = imagepub.imageList()
        for item in images:
            print item
    if 'image_add' in actions:
        imagepub.imagelist_image_add(imagelistUUID,image_key)
        return
    if 'image_key_update' in actions:
        imagepub.image_key_update(imagelistUUID, imageUuid ,image_key, image_key_value)

    if 'image_keys' in actions:
        imagepub.image_keys(imagelistUUID, imageUuid)
    if 'image_upload' in actions:
        identity = checkVoms(set(['desy']))
        if identity == None:
            log.error("No identiy found aborting")
            sys.exit(31)
        log.error("not implemented")
        log.info("Uploading '%s' with identiy '%s'" % (imageFileLocal,identity))
        upload = uploader.uploaderFacade()
        upload.uploader = 'gsidcap'
        upload.remotePrefix = "gsidcap://dcache-desy-gsidcap.desy.de:22128/pnfs/desy.de/desy/vmimages/"
        #upload.download('testing.smime', '/tmp/doof')
        #upload.upload('/tmp/doof','fooo')
        #upload.delete('fooo')
        
    if 'imagelist_import_json' in actions:
        f = open(imagelist_import_json)
        try:
            candidate = json.loads(str(f.read()))
        except ValueError:
            log.error("Failed to parse JSON.")
            sys.exit(20)
            
        if candidate == None:
            log.error("No JSON content.")
            sys.exit(21)
        
        imagepub.importer(candidate)
        

    
    
if __name__ == "__main__":
    main()
