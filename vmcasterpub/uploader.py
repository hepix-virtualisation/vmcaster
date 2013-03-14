    
import types
import uploader_dcap as uploaderDcap

from uploader_scp import uploaderScp
import re
import sys

import logging
def Property(func):
    return property(**func())

# Facade class

class uploaderFacade(object):
    """Facade class for mulitple implementations of uploader,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self.log = logging.getLogger("uploaderFacade")
        self._uploaderImp = None
        self.externalPrefix = None
    
    
    @Property
    def remotePrefix():
        doc = "The person's name"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'remotePrefix'):
                        return self._uploaderImp.remotePrefix
                    else:
                        return None
                
            return self._remotePrefix

        def fset(self, name):
            self._remotePrefix = name
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.remotePrefix = name
        def fdel(self):
            del self._remotePrefix
        return locals()
    @Property
    def uploader():
        doc = "Uploader type"

        def fget(self):
            return self._uploaderName

        def fset(self, name):
            self._uploader = name
            if name == "gsidcap":
                self._uploaderImp = uploaderDcap.uploaderDcap()
            elif name == "scp":
                self._uploaderImp = uploaderScp()
            else:
                del(self._uploaderImp)
            if hasattr(self, '_uploaderImp'):
                self._uploaderImp.remotePrefix = self.remotePrefix
            
            
        def fdel(self):
            del self._uploader
        return locals()

    
    def transforExtUri(self,externalURI):
        output = externalURI
        if self.externalPrefix == None:
            self.log.warning("External match pattern not set. This may cause configuration issues.")
            self.log.info("uri=%s" % (externalURI))
            self.log.info("match=%s" % (self.externalPrefix))
            self.log.info("replace=%s" % (self.remotePrefix))
            return output
        self.log.info("externalPrefix=%s" % (self.externalPrefix))
        self.log.info("externalURI=%s" % (externalURI))
        
        match = re.match(self.externalPrefix,externalURI)
        if match == None:
            self.log.warning("External match pattern does not match the External URI.")
            self.log.info("uri=%s" % (externalURI))
            self.log.info("match=%s" % (self.externalPrefix))
            self.log.info("replace=%s" % (self.remotePrefix))
            return output
        return re.sub(self.externalPrefix, self.remotePrefix, externalURI)
        
        
    def download(self,localpath,externalURI):
        if hasattr(self, '_uploaderImp'):
            remotepath = self.transforExtUri(externalURI)
            return self._uploaderImp.download(localpath,remotepath)
    def upload(self,localpath,externalURI):
        if hasattr(self, '_uploaderImp'):
            remotepath = self.transforExtUri(externalURI)
            return self._uploaderImp.upload(localpath,remotepath)
    def replace(self,localpath,externalURI):
        if hasattr(self, '_uploaderImp'):
            remotepath = self.transforExtUri(externalURI)
            return self._uploaderImp.replace(localpath,remotepath)
    def delete(self,externalURI):
        if hasattr(self, '_uploaderImp'):
            remotepath = self.transforExtUri(externalURI)
            return self._uploaderImp.delete(remotepath)
    
    

