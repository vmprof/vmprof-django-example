import os

import vmprof
import tempfile

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")


class Middleware(object):

    def __init__(self, application):
        self.application = application

    def _namelen(self, e):
        if e.startswith('py:'):
            return len(e.split(':')[1])
        else:
            return len(e)

    def stats(self, stats, exclude=None):
        p = stats.top_profile()
        if not p:
            return "no stats"

        stats_log = []

        p.sort(key=lambda x: x[1], reverse=True)
        top = p[0][1]

        max_len = max([self._namelen(e[0]) for e in p])

        stats_log.append("%:      name:" + " " * (max_len - 3) + "location:")

        for k, v in p:
            v = "%.1f%%" % (float(v) / top * 100)
            if v == '0.0%':
                v = '<0.1%'
            if k.startswith('py:'):
                _, func_name, lineno, filename = k.split(":", 3)

                if any([filename.startswith(ex) for ex in exclude or []]):
                    continue

                lineno = int(lineno)
                stats_log.append(
                    "%s %s %s:%d" % (v.ljust(7), func_name.ljust(max_len + 1), filename, lineno))
            else:
                stats_log.append("%s %s" % (v.ljust(7), k.ljust(max_len + 1)))

        return "\n".join(stats_log)

    def __call__(self, environ, start_response):
        prof_file = tempfile.NamedTemporaryFile()

        vmprof.enable(prof_file.fileno(), 0.0005)

        self.application(environ, start_response)

        vmprof.disable()

        stats = vmprof.read_profile(prof_file.name)

        stats_log = self.stats(stats, getattr(settings, 'VMPROF_EXCLUDE', None))

        return HttpResponse("<pre>VMprof \n\n===========\n%s</pre>" % stats_log)


application = Middleware(get_wsgi_application())
