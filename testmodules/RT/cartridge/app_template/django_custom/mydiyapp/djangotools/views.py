from django import VERSION
from django.http import HttpResponse

def display_version(request):
    return HttpResponse(VERSION, content_type='text/plain')
