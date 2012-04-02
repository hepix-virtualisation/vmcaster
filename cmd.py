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
        query_imagelists = Session.query(model.Imagelist)
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
        newImage = model.Imagelist(details,True)
        Session.add(newImage)
        Session.commit()
        return True

    def imagesDel(self,UUID):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Imagelist).\
                filter(model.Imagelist.identifier == UUID )
        for item in query_imagelists:
            Session.delete(item)
        Session.commit()
        return True




    def imagesShow(self,UUID):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Imagelist).\
                filter(model.Imagelist.identifier == UUID )
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        imagelist = query_imagelists.one()
        outModel = {}
        query_imagelistmetadata = Session.query(model.ImagelistMetadata).\
                filter(model.Imagelist.identifier == UUID ).\
                filter(model.Imagelist.id == model.ImagelistMetadata.fkImageList)
        for item in query_imagelistmetadata:
            outModel[item.key] = item.value
        query_imagelist_images = Session.query(model.Image).\
                filter(model.Imagelist.identifier == UUID ).\
                filter(model.Imagelist.id == model.Image.fkImageList)
        if query_imagelist_images.count() > 0:
            imagesarray = []
            for image in query_imagelist_images:
                imagemetadata = {u"hv:image" : str(image.identifier)}
                query_imageMetadata = Session.query(model.ImageMetadata).\
                    filter(model.Image.identifier ==  image.identifier).\
                    filter(model.Image.id == model.ImageMetadata.fkImage)
                for imageItem in query_imageMetadata:
                    imagemetadata[imageItem.key] = imageItem.value
                imagesarray.append(imagemetadata)
            outModel[u'hv:images'] = imagesarray
        
        
        outModel[u'dc:identifier'] = imagelist.identifier
        return json.dumps(outModel,sort_keys=True, indent=2)
        
    def imagelist_key_update(self,imageListUuid, imagelist_key, imagelist_key_value):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Imagelist).\
                filter(model.Imagelist.identifier == imageListUuid)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        if imagelist_key in ['dc:identifier','hv:endorser','hv:images']:
            self.log.warning("Reserved key '%s' cannot be added" % (imagelist_key))
            return None
        query_imagekeys = Session.query(model.ImagelistMetadata).\
                filter(model.Imagelist.identifier == imageListUuid).\
                filter(model.Imagelist.id == model.ImagelistMetadata.fkImageList).\
                filter(model.ImagelistMetadata.key == imagelist_key)
        if not query_imagekeys.count() == 0:
            metadata = query_imagekeys.one()
            if metadata.value != imagelist_key_value:
                metadata.value = imagelist_key_value
                Session.add(metadata)
                Session.commit()
            return imagelist_key_value
        ThisImageList = query_imagelists.one()
        newMetaData = model.ImagelistMetadata(ThisImageList.id,imagelist_key,imagelist_key_value)
        Session.add(newMetaData)
        Session.commit()
        return imagelist_key_value
    def imagelist_key_del(self,imageListUuid, imagelist_key):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.ImagelistMetadata).\
                filter(model.Imagelist.identifier == imageListUuid).\
                filter(model.Imagelist.id == model.ImagelistMetadata.fkImageList).\
                filter(model.ImagelistMetadata.key == imagelist_key)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelist key found')
            return None
        newMetaData = query_imagelists.one()
        Session.delete(newMetaData)
        Session.commit()
        return True
    def imagelist_image_add(self,imageListUuid,ImageUUID):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Imagelist).\
                filter(model.Imagelist.identifier == imageListUuid)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        query_image = Session.query(model.Image).\
                filter(model.Image.identifier == ImageUUID)
        if query_image.count() != 0:
            self.log.warning('Image alreaady exists')
            return None
        
        imagelist = query_imagelists.one()
        newimage = model.Image(imagelist.id,ImageUUID)
        Session.add(newimage)
        Session.commit()        
    def image_key_update(self,imageListUuid, imageUuid ,image_key, image_value):
        Session = self.SessionFactory()
        query_imagelists = Session.query(model.Imagelist).\
                filter(model.Imagelist.identifier == imageListUuid)
        if query_imagelists.count() == 0:
            self.log.warning('No imagelists found')
            return None
        query_image = Session.query(model.Image).\
                filter(model.Image.identifier == imageUuid)
        if query_image.count() == 0:
            self.log.warning('Image does not exist.')
            return None
        query_image_metadata = Session.query(model.ImageMetadata).\
                filter(model.Image.identifier == imageUuid).\
                filter(model.Imagelist.identifier == imageListUuid).\
                filter(model.Imagelist.id == model.Image.fkImageList).\
                filter(model.Image.id == model.ImageMetadata.fkImage).\
                filter(model.ImageMetadata.key == image_key)
        if query_image_metadata.count() == 0:
            image = query_image.one()
            newmetadata = model.ImageMetadata(image.id,image_key,image_value)
            Session.add(newmetadata)
            Session.commit()
            return True
        newmetadata = query_image_metadata.one()
        if newmetadata.value != image_value:
            newmetadata.value = image_value
            Session.add(newmetadata)
            Session.commit()
            return True
        return True
    def image_keys(self,imageListUuid, imageUuid):
        Session = self.SessionFactory()
        query_imagekeys = Session.query(model.ImageMetadata).\
                filter(model.Imagelist.identifier == imageListUuid).\
                filter(model.Imagelist.id == model.Image.fkImageList).\
                filter(model.Image.identifier == imageUuid)
        if query_imagekeys.count() == 0:
            self.log.warning('no details found')
            return None
        for item in query_imagekeys:
            print "'%s' : '%s'" % (item.key,item.value)
    
    def importer(self,dictInput):
        if not 'hv:imagelist' in dictInput.keys():
            self.log.error("JSON is not a 'hv:imagelist'")
            return False
        content = dictInput['hv:imagelist']
        if not 'dc:identifier' in content.keys():
            self.log.error("Imagelists does not contain a 'dc:identifier'")
            return False
        identifier = content['dc:identifier']
        for key in content.keys():
            if key in ['dc:identifier','hv:endorser','hv:images']:
                continue
            if isinstance(content[key], str):
                self.imagelist_key_update(identifier, key,content[key])
        if 'hv:images' in content.keys():
            for image in content['hv:images']:
                if not 'hv:image' in image.keys():
                    self.log.warning("ignoring image '%s'" % (image))
                    continue
                imagecontent = image['hv:image']
                if not 'dc:identifier' in imagecontent.keys():
                    self.log.warning("image has no ID '%s'" % (image))
                    continue
                imageIdentifier = imagecontent['dc:identifier']
                for key in imagecontent.keys():
                    if key in ['dc:identifier']:
                        continue
                    self.image_key_update(identifier, imageIdentifier ,key,imagecontent[key])
        
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
    p.add_option('--imagelist-import-smime', action ='store',help='Import an image list.', metavar='IMAGE_PATH')
    p.add_option('--imagelist-import-json', action ='store',help='Import an image list.', metavar='IMAGE_PATH')
    
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
        imagepub.imagelist_key_update(imagelistUUID, imagelist_key, imagelist_key_value)
    if 'imagelist_key_del' in actions:
        imagepub.imagelist_key_del(imagelistUUID, imagelist_key)
    
    if 'imagelist_import_smime' in actions:
        log.error("Not imprlements")
    
    if 'image_add' in actions:
        imagepub.imagelist_image_add(imagelistUUID,image_key)
        return
    if 'image_key_update' in actions:
        imagepub.image_key_update(imagelistUUID, imageUuid ,image_key, image_key_value)

    if 'image_keys' in actions:
        imagepub.image_keys(imagelistUUID, imageUuid)

    
    if 'imagelist_import_json' in actions:
        
        f = open(imagelist_import_json)
        try:
            candidate = json.loads(str(f.read()))
        except ValueError:
            log.error("Failed to parse JSON.")
            sts.exit(20)
            
        if candidate == None:
            log.error("No JSON content.")
            sys.exit(21)
        
        imagepub.importer(candidate)
        

    
    
if __name__ == "__main__":
    main()
