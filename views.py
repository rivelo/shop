# -*- coding: utf-8 -*-
from django.http import HttpResponse
import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def main_page(request):
    if request.user.is_authenticated():
    #if request.user.is_authenticated() and request.user.has_perm('accounting.type.can_vote')):
    #user = User.objects.create_user(username='test', email='jlennon@beatles.com', password='123')
    #user.save()
        return render_to_response("index.html", {"weblink": 'top.html'}, context_instance=RequestContext(request, processors=[custom_proc]))
    else:
#        return HttpResponse("Вы не можете голосовать по этому списку избирателей.")
        return render_to_response("index.html", {"weblink": 'top.html'}, context_instance=RequestContext(request, processors=[custom_proc]))
