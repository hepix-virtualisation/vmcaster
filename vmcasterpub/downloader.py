import logging

import uglyuri
import downloader_file
import downloader_http


def Property(func):
    return property(**func())


class download_facade(object):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger("retrieveFacard")
        self._retrieveImp = None
        # Detailed properties
        self._server = kwargs.get('server', None)
        self._port = kwargs.get('port', None)
        self._username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self._path = kwargs.get('path', None)
        self._trustanchor = kwargs.get('trustanchor', None)
        self._trustanchor_needed = kwargs.get('trustanchor_needed', None)
        # Set implementation
        self._uri = kwargs.get('uri', None)
        self._protocol = kwargs.get('protocol', None)


    @Property
    def protocol():
        doc = "retrieve protocol"
        def fget(self):
            return self._protocol

        def fset(self, name):
            self._protocol = name
            retrieveImpTmp = None
            if name == "http":
                retrieveImpTmp = downloader_http.downloader()
            elif name == "file":
                retrieveImpTmp = downloader_file.downloader()
            elif name == None:
                pass
            else:
                self.log.error("Invalid protocol selected '%s'" % (name))
            if retrieveImpTmp != None:
                retrieveImpTmp.server = self._server
                retrieveImpTmp.port = self._port
                retrieveImpTmp.username = self._username
                retrieveImpTmp.password = self._password
                retrieveImpTmp.path = self._path
                retrieveImpTmp.trustanchor = self._trustanchor
                retrieveImpTmp.trustanchor_needed = self._trustanchor_needed
                retrieveImpTmp.protocol = self._protocol
                self._retrieveImp = retrieveImpTmp
            else:
                if hasattr(self, '_retrieveImp'):
                    del(retrieveImpTmp)
        def fdel(self):
            del self._protocol
            self._retrieveImp = None
        return locals()



    @Property
    def server():
        doc = "server to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'server'):
                        return self._retrieveImp.server
                    else:
                        return None
            return self._server

        def fset(self, value):
            self._server = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.server = value
        def fdel(self):
            del self._server
        return locals()

    @Property
    def port():
        doc = "port to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'port'):
                        return self._retrieveImp.port
                    else:
                        return None
            return self._port

        def fset(self, value):
            if not isinstance(value, int):
                value = None
            self._port = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.port = value
        def fdel(self):
            del self._port
        return locals()

    @Property
    def username():
        doc = "username to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'username'):
                        return self._retrieveImp.username
                    else:
                        return None
            return self._username

        def fset(self, value):
            self._username = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.username = value
        def fdel(self):
            del self._username
        return locals()

    @Property
    def password():
        doc = "password to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'password'):
                        return self._retrieveImp.password
                    else:
                        return None
            return self._password

        def fset(self, value):
            self._password = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.password = value
        def fdel(self):
            del self._password
        return locals()

    @Property
    def path():
        doc = "path to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'path'):
                        return self._retrieveImp.path
                    else:
                        return None
            return self._path

        def fset(self, value):
            self._path = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.path = value
        def fdel(self):
            del self._path
        return locals()

    @Property
    def trustanchor():
        doc = "trustanchor to verify hosts against"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'trustanchor'):
                        return self._retrieveImp.trustanchor
                    else:
                        return None
            return self._trustanchor

        def fset(self, value):
            self._trustanchor = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.trustanchor = value
        def fdel(self):
            del self._trustanchor
        return locals()

    @Property
    def trustanchor_needed():
        doc = "trustanchor_needed to verify hosts against"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'trustanchor_needed'):
                        return self._retrieveImp.trustanchor_needed
                    else:
                        return None
            return self._trustanchor_needed

        def fset(self, value):
            self._trustanchor_needed = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.trustanchor_needed = value
        def fdel(self):
            del self._trustanchor_needed
        return locals()


    @Property
    def uri():
        doc = """uri to use
        Conveniance function and handles uris"""
        def fget(self):
            if self.protocol == None:
                return None
            userPass = ""
            if self.username != None:
                userPass = self.username
                if self.password == None:
                    userPass = self.username
                else:
                    userPass = "%s:%s" % (self.username, self.password)
            hostPort = ""
            if self.server != None:
                if self.port == None:
                    hostPort = self.server
                else:
                    hostPort = "%s:%s" % (self.server, self.port)
            netloc = ""
            if (len(hostPort) > 0):
                if (len(userPass) > 0):
                    netloc = "%s@%s" % (userPass, hostPort)
                else:
                    netloc = hostPort
            path = ""
            if self.path != None:
                path = self.path
            output = "%s://%s%s" % (self.protocol,netloc,path)
            return output

        def fset(self, value):
            if isinstance(value,  unicode):
                value = str(value)
            if not isinstance(value,  str):
                value = ""
            parseddict = uglyuri.uglyUriParser(value)
            protocol = parseddict.get('scheme')
            self.protocol = protocol
            path = parseddict.get('path')
            self.path = path
            port = parseddict.get('port')
            if len(port) == 0:
                port = 80
            self.port = port
            server = parseddict.get('hostname')
            self.server = server

        def fdel(self):
            pass
        return locals()

    def requestAsString(self):
        if hasattr(self, '_retrieveImp'):
            if self._retrieveImp != None:
                return self._retrieveImp.requestAsString()
            else:
                self.log.critical("programming error no protocol is None")
        else:
            self.log.critical("programming error no protocol implementation")
        return None




def downloader(uri):
    dl_f = download_facade()
    dl_f.uri = uri
    return dl_f.requestAsString()
