import dishpub.uploader_dcap as dcapuploader
import dishpub.uploader as uploader


if __name__ == "__main__" :
    u1 = uploader.uploaderFacade()
    
    
    u1.remotePrefix = 'frog'
    #print u1.remotePrefix 
    u1.uploader = 'gsidcap'
    #print u1.uploader
    #print dir(u1)
    u1.upload('foo','feng')
    
    u1.uploader = 'gsidcap'
    #print dir(u1)
    u1.remotePrefix = 'frog'
    
    u1.upload('foo','feng')
