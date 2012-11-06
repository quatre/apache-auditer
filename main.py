from parser import Context, Site
import re
import logging
import os
import glob

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ApacheConf(object):

    def parse_file(self, path):
        fd = open(path, "r")
        logger.debug("Opened %s" % path)
        for line in fd.readlines():
            line = line.strip()
            if len(line) == 0:
                self.blanks += 1
                continue
            if line.startswith("#"):
                self.comments += 1
                #Comment!
                continue
            match = re.match("<([^/]\S+)\s+(.*)>", line)
            if match:
                #Context
                if re.match("VirtualHost", match.group(1)):
                    #Vhost
                    new_context = Site(match.group(2))
                    self.vhosts.append(new_context)
                    logger.info("New VHost")
                else:
                    logger.info("New context %s" % match.group(1))
                    new_context = Context(":".join([match.group(1), match.group(2)]))
                self.context_stack[0].add_context(new_context)
                self.context_stack.insert(0, new_context)
                #We're done here!
                continue
            match = re.match("</(\S+)>", line)
            if match:
                logger.info("End of context %s" % match.group(1))
                #Popping out of context!
                self.context_stack.pop(0)
                #We're done here!
                continue
            args = re.split("\s+", line)
            directive = args.pop(0)
            self.context_stack[0].add_directive(directive, args)
            logger.info("Directive %s : (%s)" % (directive, ", ".join(args)))
            if directive == "Include":
                logger.debug("Including a file!")
                try:
                    serverroot = self.context_stack[-1].get_directive("ServerRoot")
                except:
                    serverroot = os.path.dirname(self.config_path)
                included_paths = glob.glob(os.path.join(serverroot, args[0]))
                for included_path in included_paths:
                    for root, dirs, files in os.walk(included_path):
                        [self.parse_file(os.path.join(root, name)) for name in files]
        logger.debug("Done parsing %s!" % path)
        fd.close()
                


    def __init__(self, config_path="/etc/apache2/apache2.conf"):
        self.comments = 0
        self.blanks = 0
        self.config_path = config_path
        self.main_file = open(config_path, "r")
        self.context_stack = [Context(type="global")]
        self.vhosts = []

        


def report(conf):
    print "Audit report for Apache server configuration"
    print "Main configuration facts :"
    for k in ["AccessFileName", "CustomLog", "ErrorLog", "KeepAlive", "KeepAliveTimeout", "MaxKeepAliveRequests"]:
        try:
            v = conf.context_stack[0].get_directive(k)
        except KeyError:
            v = "N/A"
        print "\t%s => %r" % (k, v)

    print "Sites : "
    for s in conf.vhosts:
        print "Site %s" % s.name
        print "\tAliases : "
        for a in s.serverAliases:
            print "\t\t %s" % a
        print "DocumentRoot : %s" % s.documentRoot






if __name__ == "__main__":
    apacheconf = ApacheConf()
    apacheconf.parse_file(apacheconf.config_path)

