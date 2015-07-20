import httplib
from django.conf.urls import url
from django.http import HttpResponse


def cpu_1():
    return [b for b in range(10000000)]


def cpu_2():
    return [b for b in range(20000000)]


def io_1():
    conn = httplib.HTTPConnection("httpbin.org")
    conn.request("GET", "/delay/1")
    return conn.getresponse()


def index(request):

    # long cpu 1
    cpu_1()

    # long cpu 2
    cpu_2()

    # long IO
    io_1()

    return HttpResponse("OK")


urlpatterns = [
    url(r'^', index)
]
