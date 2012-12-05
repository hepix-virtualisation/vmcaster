import ConfigParser
import sys
import logging, logging.config


if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json

class jsonConfigParser(ConfigParser.SafeConfigParser):
    def __init__(self):
        self.log = logging.getLogger("vmCtrl.jsonConfigParser")
        ConfigParser.SafeConfigParser.__init__(self)
    def getJson(self,section,option):
        value = unicode(self.get(section,option))
        try:
            return json.loads(value)
        except ValueError:
            self.log.warning("Could not parse json value from section '%s' and key '%s'" % (section,option))
            return None
