import urllib2, urllib, base64
import sys, string, os, getopt
import getpass

vmcappdburl = 'https://vmcaster.appdb-dev.marie.hellasgrid.gr/vmlist/submit/sso/'

def postdata(username, password, imagelist):
   passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
   passman.add_password(None, vmcappdburl, username, password)
   authhandler = urllib2.HTTPBasicAuthHandler(passman)
   opener = urllib2.build_opener(authhandler)
   urllib2.install_opener(opener)

   f = open(imagelist, 'r')
   file_data = base64.b64encode(f.read())

   postdata=[('published','false'),('file',file_data)]

   postdata=urllib.urlencode(postdata)
   req=urllib2.Request(vmcappdburl, postdata)
   req.add_header("Content-type", "application/x-www-form-urlencoded")
   page=urllib2.urlopen(req).read()
   print page


#postdata(username, password, imagelist)

class uploaderScp:
    def __init__(self):
        self.remotePrefix = None
        self.log = logging.getLogger("uploaderEgiAppDb")
    def _getfilepath(self,remotePath):
        if self.remotePrefix != None:
            return self.remotePrefix + remotePath
        else:
            return remotePath
    def exists(self,remotePath):
        prefix = self.remotePrefix.split(":")
        fuill = "%s/%s" % (prefix[1],remotePath)
        cmd = "ssh %s stat %s" % (prefix[0],fuill)
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
