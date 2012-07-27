# Makes things in right format.

import ConfigParser, os
import logging
import uploader

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



class hostUploader:
    def __init__(self,cfgFile):
        self.log = logging.getLogger("hostUploader")
        self.config = ConfigParser.ConfigParser()
        self.config.read(cfgFile)
        self.allHosts = {}
        for section in self.config.sections():
            writeProto = None
            if self.config.has_option(section, 'writeprotocol'):
                writeProto = self.config.get(section,'writeprotocol')
            else:
                self.log.error("Section '%s' is missing a 'writeprotocol' config setting." % (section))
                continue
            serverName = None
            if self.config.has_option(section, 'server'):
                serverName = self.config.get(section,'server')
            else:
                self.log.error("Section '%s' is missing a 'server' config setting." % (section))
                continue
            writePrefix = None
            if self.config.has_option(section, 'writeprefix'):
                writePrefix = self.config.get(section,'writeprefix')
            else:
                self.log.error("Section '%s' is missing a 'writeprefix' config setting." % (section))
                continue
            readPrefix = None
            if self.config.has_option(section, 'readprefix'):
                readPrefix = self.config.get(section,'readprefix')
            else:
                self.log.error("Section '%s' is missing a 'readprefix' config setting." % (section))
                continue
            self.allHosts[serverName] = {'serverName' : serverName,
                'writeProto' : writeProto,
                'writePrefix' : writePrefix,
                'readPrefix' : readPrefix}
            
    def replaceFile(self,localPath,remoteHost,remotePath):
        if not remoteHost in self.allHosts:
            raise InputError("Host '%s' is not known" % remoteHost)
        
        if not os.path.isfile(localPath):
            raise InputError("file not found at localpath '%s'" % localPath)
        u1 = uploader.uploaderFacade()
        u1.uploader = self.allHosts[remoteHost]["writeProto"]
        u1.remotePrefix = self.allHosts[remoteHost]["writePrefix"]
        return u1.replace(localPath,remotePath)   
    def uploadFile(self,localPath,remoteHost,remotePath):
        if not remoteHost in self.allHosts:
            raise InputError("Host '%s' is not known" % remoteHost)
        
        if not os.path.isfile(localPath):
            raise InputError("file not found at localpath '%s'" % localPath)
        u1 = uploader.uploaderFacade()
        u1.uploader = self.allHosts[remoteHost]["writeProto"]
        u1.remotePrefix = self.allHosts[remoteHost]["writePrefix"]
        return u1.upload(localPath,remotePath)
    def deleteFile(self,remoteHost,remotePath):
        if not remoteHost in self.allHosts:
            raise InputError("Host '%s' is not known" % remoteHost)
        u1 = uploader.uploaderFacade()
        u1.uploader = self.allHosts[remoteHost]["writeProto"]
        u1.remotePrefix = self.allHosts[remoteHost]["writePrefix"]
        return u1.delete(remotePath)
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    obj = hostUploader('publisher.cfg')
    #obj.uploadFile('/etc/fstab','dish.desy.de','dfsdfsdf')
    obj.delete('dfsdfsdf')
