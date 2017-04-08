import downloader_base
import base64
import httplib
import socket
import logging


log = logging.getLogger(__name__)


class downloader(downloader_base.downloader):
    def __init__(self):
        downloader_base.downloader.__init__(self)
        self.port_default = 80

    def requestAsString(self):
        output = {'code' : 0}
        auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
        timeout = 60
        con = httplib.HTTPConnection(self.server, self.port, True, timeout)
        headers = {"User-Agent": "vmcatcher"}
        if (self.username != None) and (self.password != None):
            auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
            headers["Authorization"] = "Basic %s" % (auth)
        try:
            con.request("GET" , self.path, headers=headers)
        except socket.gaierror as exp:
            output['error'] = exp.strerror
            output['code'] = 404
            log.error("Failed to connect to %s:%s error %s:%s" % (self.server,self.port, output['code'], output['code']))
            return output
        except socket.error as exp:
            output['error'] = exp.strerror
            output['code'] = 404
            log.error("Failed to connect to %s:%s error %s:%s" % (self.server,self.port, output['code'], output['code']))
            return output
        responce =  con.getresponse()
        httpstatus = responce.status
        if httpstatus == 200:
            output['responce'] = responce.read()
        else:
            output['error'] = responce.reason
            output['code'] = httpstatus
        return output

