import urlparse 
import subprocess
import time
import logging
import os




def runpreloadcommand(cmd,timeout,preload):
    newenv = dict(os.environ)
    newenv["LD_PRELOAD"] = preload
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=newenv)
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
    
    return (processRc,stdout,stderr)

def gsiDcapCopy(src,dest,timeout = 60):
    cmd = "dccp -C 3000 -d 2 -A %s %s" % (src,dest)
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
        log = logging.getLogger("gsiDcapCopy")
        log.error("failed to execute command '%s'" % (cmd))
    return (processRc,stdout,stderr)



class uploaderDcap:
    def __init__(self):
        self.remotePrefix = None
        self.log = logging.getLogger("uploaderGsiDcap")
    def _getfilepath(self,remotePath):
        if self.remotePrefix != None:
            return self.remotePrefix + remotePath
        else:
            return remotePath
    def exists(self,remotePath):
        cmd = "stat %s" % (self._getfilepath(remotePath))
        timeout = 10
        preload = "/usr/lib64/libpdcap.so.1"
        return runpreloadcommand(cmd,timeout,preload)
        
    def delete(self,remotePath):
        cmd = "unlink %s" % (self._getfilepath(remotePath))
        timeout = 10
        preload = "/usr/lib64/libpdcap.so.1"
        return runpreloadcommand(cmd,timeout,preload)
        
    def upload(self,localpath,remotePath):
        path = self._getfilepath(remotePath)
        return gsiDcapCopy(localpath,path)

    def replace(self,localpath,remotePath):
        path = self._getfilepath(remotePath)
        (rc,stdout,stderr) =  self.exists(path)
        if rc == 0:
            (rc,stdout,stderr) = self.delete(path)
            if rc != 0:
                print stderr
                return (rc,stdout,stderr)
        rc,stdout,stderr = gsiDcapCopy(localpath,path)
        if rc != 0:
            print stderr
            return (rc,stdout,stderr)
        return (rc,stdout,stderr)
    def download(self,remotePath,localpath):
        rc,stdout,stderr = gsiDcapCopy(self._getfilepath(remotePath),localpath)
        if rc != 0:
            for errorLine in stderr.split('\n'):
                self.log.error("stderr:'%s'" % (errorLine))
        return rc,stdout,stderr
