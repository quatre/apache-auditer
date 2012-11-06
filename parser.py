import os.path
from disk_usage import disk_usage


class Context(object):

    def __init__(self, name=None, type=None):
        self._name = name
        self.directives = {}
        self.subcontexts = {}
        self.type = type
        self._size = None

    def add_context(self, context):
        name = context._name
        if name not in self.subcontexts.keys():
            self.subcontexts[name] = []
        self.subcontexts[name].append(context)

    def add_directive(self, directive, args=None):
        if directive not in self.directives.keys():
            self.directives[directive] = []
        self.directives[directive].append(args)

    @property
    def aliases(self):
        return self.directives["Alias"]

    @property
    def name(self):
        return self._name

    def get_directive(self, name):
        return self.directives[name][0][0]


class Site(Context):

    @property
    def name(self):
        try:
            return self.directives["ServerName"][0][0]
        except KeyError:
            return "__default__"

    @property
    def documentRoot(self):
        try:
            return self.directives["DocumentRoot"][0][0]
        except KeyError:
            return None

    @property
    def serverAliases(self):
        try:
            return self.directives["ServerAlias"][0]
        except KeyError:
            return []

    @property
    def size(self):
        if self._size:
            return self._size
        paths = [self.documentRoot,] + [a[1] for a in self.aliases]
        paths = list(set([os.path.abspath(path.strip('"')) for path in paths]))
        paths.sort()
        for x_path in paths[:]:
            for y_path in paths[:]:
                if x_path is y_path:
                    continue
                if os.path.commonprefix([x_path, y_path]) == x_path:
                    paths.remove(y_path)
        size = 0
        for path in paths:
            size += disk_usage(path)
        self._size = size

