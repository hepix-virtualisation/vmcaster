import urllib2, urllib, base64
import sys, string, os, getopt
import getpass
import logging
import getpass
import uglyuri
import json

def createXMLwrapper(actionList, entity, username, response, imagelist_data):
    actionLines = ""
    for action in actionList:
        actionLines += "<action><![CDATA[%s]]></action>" % (action)
    xmlTemplate = """<?xml version="1.0" encoding="utf-8"?><appdbvmc>%(actionLines)s<entity><![CDATA[%(entity)s]]></entity><response><![CDATA[%(response)s]]></response><user><![CDATA[%(username)s]]></user><imagelist><![CDATA[%(imagelist_data)s]]></imagelist></appdbvmc>"""
    data = {'actionLines': actionLines, 
        'entity': entity,
        'response' : response,
        'username' : username,
        'imagelist_data' : imagelist_data}
    return xmlTemplate%data

def postdata(uri,username, password, imagelist, actionList, entity, response):
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, uri, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    f = open(imagelist, 'r')
    file_data = base64.b64encode(f.read())
    data=createXMLwrapper(actionList, entity, username, response, file_data)
    postdata=[('data',data)]
    postdata=urllib.urlencode(postdata)
    req=urllib2.Request(uri, postdata)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    try:
        page=urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
        return e.code,"",e.reason
    return 0,page,""

 
#postdata(username, password, imagelist)


def parseResultSuccess(inputStr):
    log = logging.getLogger("parseResultSuccess")
    parsedJson = json.loads(inputStr)
    if parsedJson == None:
        log.error("Invalid Json")
        return None
        
    if not isinstance( parsedJson, dict ):
        log.error("Json does not encode a dictionary")
        return None
    if not "egiappdb" in parsedJson.keys():
        log.error("Json does not encode egiappdb protocol")
        return None
    if not isinstance( parsedJson["egiappdb"], dict ):
        log.error("Json does not encode egiappdb as dict")
        return None
    reqfieldsStr = set(['status','details'])
    reqfieldsInt = set(['submission_id'])
    
    for reqKey in reqfieldsStr.union(reqfieldsInt):
        if not reqKey in parsedJson["egiappdb"].keys():
            log.error("Json does not encode egiappdb:%s" % (reqKey))
            return None
    for reqKey in reqfieldsStr:
        if not isinstance( parsedJson["egiappdb"][reqKey], unicode ):
            log.error("Json does not encode as a string egiappdb:%s" % (reqKey))
            return None
    for reqKey in reqfieldsInt:
        if not isinstance( parsedJson["egiappdb"][reqKey], int ):
            log.error("Json does not encode as a int egiappdb:%s" % (reqKey))
            return None
    return {"status" : parsedJson["egiappdb"]["status"],
        "details" : parsedJson["egiappdb"]["details"],
        "submission_id" : parsedJson["egiappdb"]["submission_id"],
    }
    
def parseFlags(flags):
    log = logging.getLogger("parseFlags")
    output = []
    for aflag in flags:
        if not aflag.startswith("egiappdb:"):
            log.debug("ignoring flag '%s'" % (aflag))
            continue
        splitLine = aflag[9:].split('=')
        if len(splitLine) != 2:
            log.debug("ignoring flag '%s' as no '=' sign." % (aflag))
            continue
        if splitLine[1] != 'true':
            log.debug("ignoring flag '%s' as value != 'true'." % (aflag))
            continue
        output.append(splitLine[0])
    return output
    
class uploaderEgiAppDb:
    def __init__(self):
        self.remotePrefix = None
        self.log = logging.getLogger("uploaderEgiAppDb")
    def _getfilepath(self,remotePath):
        if self.remotePrefix != None:
            return self.remotePrefix + remotePath
        else:
            return remotePath
    def exists(self,remotePath):
        return 1,"",""
        
    def delete(self,remotePath):
        return 0,"",""
        
    def upload(self,localpath,remotePath):
        for line in open(localpath):
            print line
        return self.replace(localpath,remotePath)

    def replace(self,localpath,remotePath):
        self.log = logging.getLogger("uploaderEgiAppDb.replace")
        signedFile = ""
        actionList = parseFlags(self.flags)
        for line in open(localpath):
            signedFile += line
        self.log.debug("localpath:%s" % (localpath))
        self.log.debug("remotePath:%s" % (remotePath))
        
        uriParsed = uglyuri.uglyUriParser(remotePath)
        if uriParsed["user"] == None:
            return 1,"","Remote uri does not assign an upload user" 
        if uriParsed["scheme"] != "egiappdb":
            return 1,"","Remote uri protocol is not 'egiappdb'" 
        
        
        
        self.log.debug("actionList:%s" % (actionList))
        if len(actionList) == 0:
            actionList = ['insert']
            flagstringL = []
            for actionItem in actionList:
                flagstringL.append("egiappdb:%s=true" % (actionItem))
            self.log.warning("No flags set for upload, defaulting flags to %s" % (flagstringL))
        
        
        newUriComponents = {
            "scheme" : "https",
            "path" : uriParsed["path"],
            "hostname" : uriParsed["hostname"],
            "port" : uriParsed["port"],
        }
        username = uriParsed["user"]
        newUri = uglyuri.uglyUriBuilder(newUriComponents)
        self.log.debug("Uploading uri:%s" % (newUri))
        password = getpass.getpass("Appdb password for '%s':" % (username))
        entity = 'imagelist'
        response = 'json'
        output = postdata(newUri,username, password, localpath, actionList, entity, response)
        rc,stdout,stderr = output
        if rc == 0:
            self.log.info("Output:%s" % (str(output)))
        if rc != 0:
            return (rc,stdout,stderr)
        parsedResult = parseResultSuccess(stdout)
        if parsedResult == None:
            return (2,stdout,stderr)
        rc = 0
        if parsedResult["status"] != "success":
            rc = 3
        #print("status:%s" % (parsedResult["status"]))
        print("details:%s" % (parsedResult["details"]))
        print("submission_id:%s" % (parsedResult["submission_id"]))
        
        return (rc,stdout,stderr)
    def download(self,remotePath,localpath):
        self.log = logging.getLogger("uploaderEgiAppDb.download")
        cmd = "scp %s %s" % (remotePath,localpath)
        self.log.info("Attempting:%s" % (cmd))
        rc,stdout,stderr = runpreloadcommand(cmd,10)
        if rc != 0:
            self.log.debug(cmd)
            self.log.error( stderr)
            return (rc,stdout,stderr)
        return (rc,stdout,stderr)
