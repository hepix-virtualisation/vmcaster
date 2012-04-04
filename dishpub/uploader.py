    
import types
import dishpub.uploader_dcap as uploaderDcap

def Property(func):
    return property(**func())

# Facade class

class uploaderFacade(object):
    """Facade class for mulitple implementations of uploader,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self._uploaderImp = None
    @Property
    def remotePrefix():
        doc = "The person's name"

        def fget(self):
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
                
            else:
                self._uploaderImp = None
            if self._uploaderImp != None:
                self._uploaderImp.remotePrefix = self.remotePrefix
            
            
        def fdel(self):
            del self._uploader
        return locals()
    def __init__(self) :
        pass
    
    def download(self,localpath,remotepath):
        return self._uploaderImp.download(localpath,remotepath)
    def upload(self,localpath,remotepath):
        return self._uploaderImp.upload(localpath,remotepath)
    def replace(self,localpath,remotepath):
        return self._uploaderImp.replace(localpath,remotepath)

    
    
    

