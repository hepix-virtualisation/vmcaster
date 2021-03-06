import urlparse

def uglyUriParser(uri):
    parsedUri = urlparse.urlsplit(uri)
    if isinstance(parsedUri, tuple):
        # We are probably python 2.4
        hostname = parsedUri.hostname
        user = parsedUri.username
        port = ""
        if parsedUri.port != None:
            port = parsedUri.port
        return { "scheme" : parsedUri[0],
            "path" : parsedUri[2],
            "hostname" : hostname,
            "port" : port,
            "user" : user
        }
    if isinstance(parsedUri,urlparse.SplitResult):
        # We are probably python 2.6
        return { "scheme" : parsedUri.scheme,
            "path" : parsedUri.path,
            "hostname" : parsedUri.hostname,
            "port" : parsedUri.port,
        }

def uglyUriBuilder(components):
    if not isinstance(components, dict):
        #We only process dictionaries
        return None
    if not 'scheme' in components:
        #Need the protocol
        return None
    if not 'hostname' in components:
        #Need the hostname
        return None
    output = "%s://%s" % (components['scheme'],components['hostname'])
    if 'port' in components:
        if components['port'] != '':
        
            output += ":%s" % (components['port'])
    if 'path' in components:
        output +=  "%s" % (components['path'])
    return output
    
        
        
    
