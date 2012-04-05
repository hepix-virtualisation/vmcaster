import dishpub.uploader_dcap as dcapuploader
import dishpub.uploader as uploader


if __name__ == "__main__" :
    u1 = uploader.uploaderFacade()
    
    
    u1.remotePrefix = 'gsidcap://dcache-desy-gsidcap.desy.de:22128/pnfs/desy.de/desy/vmimages/'
    
    u1.uploader = 'gsidcap'
    #rc,stdout,stderr = u1.upload('/etc/fstab','feng')
    #if rc != 0:
    #    print rc
    #    print stdout
    #    print stderr
    u1.delete('feng')
