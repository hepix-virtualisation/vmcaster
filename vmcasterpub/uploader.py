    
import types
import uploader_dcap as uploaderDcap
import uploader_egiappdb as uploaderEgiAppDb


from uploader_scp import uploaderScp
from uploader_local import uploaderLocal


import re
import sys

import logging
def Property(func):
    return property(**func())

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
        
# Facade class

class uploaderFacade(object):
    """Facade class for mulitple implementations of uploader,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self.log = logging.getLogger("uploaderFacade")
        self._uploaderImp = None
        self._flags = None
        self.externalPrefix = None
    def HasImplementation(self):
        if hasattr(self, '_uploaderImp'):
            return True
        else:
            return False
    
    @Property
    def remotePrefix():
        doc = "Remote upload prefix"

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
    def flags():
        doc = "Flags for upload"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'flags'):
                        return self._uploaderImp.flags
            return self._flags

        def fset(self, name):
            self._flags = name
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.flags = name 
        def fdel(self):
            del self._flags
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
            elif name == "egiappdb":
                self._uploaderImp = uploaderEgiAppDb.uploaderEgiAppDb()
            elif name == "local":
                self._uploaderImp = uploaderLocal()
            else:
                self.log.error("Invalid upload protocol sellected '%s'" % (name))
                self.log.info('Valid upload protocols are ["local","scp","gsidcap","egiappdb"]')
                
                del(self._uploaderImp)
            if hasattr(self, '_uploaderImp'):
                self._uploaderImp.remotePrefix = self.remotePrefix
                self._uploaderImp.flags = self.flags
            else:
                errorMsg = str("Invalid upload protocol sellected:'%s'" % (name))
                error = InputError("Invalid Value")
                raise error
            
            
        def fdel(self):
            del self._uploader
        return locals()

    
    def transforExtUri(self,externalURI):
        output = externalURI
        if self.externalPrefix == None:
            self.log.error("External match pattern not set. This may cause configuration issues.")
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
    
    

