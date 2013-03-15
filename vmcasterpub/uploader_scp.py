import urlparse 
import subprocess
import time
import logging
import os


def runpreloadcommand(cmd,timeout):
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
    return (processRc,stdout,stderr)



class uploaderScp:
    def __init__(self):
        self.remotePrefix = None
        self.log = logging.getLogger("uploaderScp")
    def _getfilepath(self,remotePath):
        if self.remotePrefix != None:
            return self.remotePrefix + remotePath
        else:
            return remotePath
    def exists(self,remotePath):
        prefix = self.remotePrefix.split(":")
        fuill = "%s/%s" % (prefix[1],remotePath)
        cmd = "ssh %s stat %s" % (prefix[0],fuill)
        print cmd
        timeout = 10
        return runpreloadcommand(cmd,timeout)
        
    def delete(self,remotePath):
        prefix = self.remotePrefix.split(":")
        fuill = "%s/%s" % (prefix[1],remotePath)
        
        cmd = "ssh %s rm %s" % (prefix[0],fuill)
        timeout = 10
        return runpreloadcommand(cmd,timeout)
        
    def upload(self,localpath,remotePath):
        self.log = logging.getLogger("uploaderScp.upload")
        cmd = "scp %s %s" % (localpath,remotePath)
        self.log.info("Attempting:%s" % (cmd))
        rc,stdout,stderr = runpreloadcommand(cmd,10)
        if rc != 0:
            self.log.debug(cmd)
            self.log.error( stderr)
            return (rc,stdout,stderr)
        return (rc,stdout,stderr)
        return self.replace(localpath,remotePath)

    def replace(self,localpath,remotePath):
        self.log = logging.getLogger("uploaderScp.replace")
        cmd = "scp %s %s" % (localpath,remotePath)
        self.log.info("Attempting:%s" % (cmd))
        rc,stdout,stderr = runpreloadcommand(cmd,10)
        if rc != 0:
            self.log.debug(cmd)
            self.log.error( stderr)
            return (rc,stdout,stderr)
        return (rc,stdout,stderr)
    def download(self,remotePath,localpath):
        self.log = logging.getLogger("uploaderScp.download")
        cmd = "scp %s %s" % (remotePath,localpath)
        self.log.info("Attempting:%s" % (cmd))
        rc,stdout,stderr = runpreloadcommand(cmd,10)
        if rc != 0:
            self.log.debug(cmd)
            self.log.error( stderr)
            return (rc,stdout,stderr)
        return (rc,stdout,stderr)
