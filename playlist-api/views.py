"""
 Copyright 2011 Alexander Forselius

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. 
"""
# Create your views here.
# coding=utf-8
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest,HttpResponseRedirect
from django.template import RequestContext
from playlist_api.models import *
from django.db import models
from django.contrib.admin import *
from urlparse import urlparse
from django.core.urlresolvers import resolve
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.csrf import *    
from django.contrib import *
from oauth_playlist_api import *
from datetime import *
from random import *
import datetime
import md5
import json
import logging
import urllib
from django.contrib.auth import *
from django.contrib.auth.models import *
from django.forms.models import ModelForm
from random import random
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
class ChannelForm(ModelForm):
    class Meta:
        exclude = ('user')
        model = Channel
class HttpResponseRedirectView(HttpResponseRedirect):
    """
        This response directs to a view by reversing the url
    
        e.g. return HttpResponseRedirectView('org.myself.views.myview') 
        or use the view object e.g.
             from org.myself.views import myview
             return HttpResponseRedirectView(myview)
        
        You can also pass the url arguments to the constructor e.g.
        return HttpResponseRedirectView('org.myself.views.myview', year=2008, colour='orange')
    """
    def __init__(self, view, *args, **kwargs):
        viewurl = reverse(view, args=args, kwargs=kwargs)
        HttpResponseRedirect.__init__(self, viewurl)
class AppForm(ModelForm):
    class Meta:
        model = OAuthApplication
        exclude = ('user','secret_key','public_key')
class UserForm(forms.Form):
    username = forms.SlugField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    retype_password = forms.CharField(widget=forms.PasswordInput)
    
def playlist(request,slug):
    _playlist = Playlist.objects.get(slug=slug)
    if(_playlist.public or _playlist.user == request.user):
        return render_to_response('mc/playlist.xml',{'playlist':_playlist})
def terms_of_conditions(request):
	return render_to_response('mc/tos.xml',{},context_instance=RequestContext(request))
def index(request):
    channels = Channel.objects.all().order_by('-id')[:6]
    return render_to_response('mc/index.xml',{'channels':channels},context_instance=RequestContext(request))
def add_app_view(request):
    """ Adds an app """
    form = AppForm()
    return render_to_response('mc/apps_add.xml',{'form':form},RequestContext(request))
def add_app_do(request):
    form = AppForm(request.POST)
   
    f = form.save(commit=False)
    f.user_id = request.user.id
    f.secret_key = md5.new('secret$%s$%s' % (random(), f.user_id)).hexdigest()
    f.public_key = md5.new('public$%s$%s' % (random(), f.user_id)).hexdigest()
    f.save() 
    form.save()
    return HttpResponseRedirect('../../apps')
def spotifyapps(request, app, par):
    validated = False
    if 'validated' in request.GET:
        validated = True
    return render_to_response('mc/spotifyapps.xml', {'app':app, 'parameter': par, 'validated' : validated})
def content_import(request):
    """
    Import content from sources
    """
    url = request.GET['url']
    
    if url.startswith('https://') or url.startswith('http://'):
        c = urllib.urlopen(url)
        
        r = HttpResponse(c,mimetype='text/xml')
        r['X-Frame-Options'] = 'GOFORIT'
        return r
    else:
        c = urllib.urlopen('https://gdata.youtube.com/feeds/api/videos?q=%s&num=620&output=rss' % (url))
        r = HttpResponse(c,mimetype='text/xml')
        r['X-Frame-Options'] = 'GOFORIT'
        return r
def app_log_view(request,app_id):
    """ App log view """
    _app = OAuthApplication.objects.get(id=app_id,user=request.user)
    logs = OAuthEvent.objects.filter(app=_app)
    return render_to_response('mc/apps_log.xml',{'app': _app,'logs':logs},context_instance=RequestContext(request))
def channel_list(request):
    """
    List of channels
    """
    channels = Channel.objects.filter(user = request.user)
    return render_to_response('mc/channels.xml',{'channels':channels},context_instance=RequestContext(request))
def channel_form(request, id=-1):
    form = ChannelForm()
    if id > 0:
        form = ChannelForm(Channel.objects.get(id = request.POST['id']))
    return render_to_response('mc/channel_edit.xml',{'form':form},context_instance=RequestContext(request))
def add_channel_do(request):
    form = ChannelForm(request.POST)
    channel = form.save(False)
    channel.user = request.user
    channel.save()
    return HttpResponseRedirect(reverse('myproject.mediachrome.views.channel_list'))

def channel(request,user_name,id):
    """
    An virtual TV channel
    """
    channel_id = id

    channel = Channel.objects.get(id = channel_id)
    pos = 0
    clip_length = channel.clip_length
    if 'pos' in request.GET:
        pos = request.GET['pos']
    if channel.random:
        pos = -2
    # now check something important, convert all http links to rss strema
    
     

    a = render_to_response('mc/channel.xml',{'channel':channel,'pos':pos,'clip_length':clip_length},context_instance=RequestContext(request))
    a['X-Frame-Options'] = 'GOFORIT'
    return a
def signup(request):
    """ Signs up an user """
    form = UserForm()
    return render_to_response('mc/signup.xml',{'form':form},context_instance=RequestContext(request))
def signup_do(request):
    form = UserForm(request.POST)
    if form.is_valid():
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		email = form.cleaned_data['email']
		retype_password = form.cleaned_data['retype_password']
		if password == retype_password and form.cleanded_data['tos'] == 'accepted':
			user = User.objects.create_user(username,email,password)
			user.save()
			return HttpResponseRedirect("..")
    return HttpResponseRedirect("..")
def oauth_help_content(request):
	return render_to_response('mc/oauth_help_content.xml',{},context_instance=RequestContext(request))

def oauth_help(request):
	return render_to_response('mc/oauth_help.xml',{},context_instance=RequestContext(request))
def oauth_help_auth(request):
	return render_to_response('mc/oauth_help_auth.xml',{},context_instance=RequestContext(request))
def app_detail_view(request,app_id):
    """ App details view """
    app = OAuthApplication.objects.get(id=app_id,user=request.user)
    form = AppForm(instance=app)
    
    return render_to_response('mc/app_details.xml',{'app':app,'form':form},context_instance=RequestContext(request))
def apps_view(request):
    """ Gets your apps """
    apps = OAuthApplication.objects.filter(user=request.user)
    return render_to_response("mc/apps_home.xml",{'apps':apps},context_instance=RequestContext(request))
def login_do(request):
    _username = request.POST['username']
    _password = request.POST['password']
    user = authenticate(username=_username,password=_password)
        
    if user is not None:
        if user.is_active:
            login(request,user)
            if 'oauth_mode' in request.POST:
               return HttpResponseRedirect(reverse("myproject.mediachrome.views.oauth")+"?client_id=%s&redirect_uri=%s" % (request.POST['client_id'],request.POST['redirect_uri']))
			
            # if in oauth mode, return next
            return HttpResponseRedirectView('myproject.mediachrome.views.index')
    else:
        if 'oauth_mode' in request.POST:
            return HttpResponseRedirect(reverse("myproject.mediachrome.views.oauth")+"?wrong_password=true&client_id=%s&redirect_uri=%s" % (request.POST['client_id'],request.POST['redirect_uri']))
   
        return HttpResponseRedirect("%s?%s" % (reverse('myproject.mediachrome.views.login_view'), "wrong_password=true"))
def login_view(request):
	"""
	Login visual view
	"""
	return render_to_response('mc/login.xml',{},context_instance=RequestContext(request))
def logout_do(request):
    logout(request)
    return HttpResponseRedirect('..')
def oauth(request):
    """ OAuth request """
    client_id = request.GET['client_id']
    redirect_uri = request.GET['redirect_uri']
    # Get client app    
    app = OAuthApplication.objects.get(public_key=client_id)
    return render_to_response('mc/oauth.xml',{'app':app,'client_id':client_id,'redirect_uri':redirect_uri},context_instance=RequestContext(request))

def oauth_do(request):
    """ Grant or disgrant an oauth operation """
    your_url = request.POST['redirect_uri']
    client_id = request.POST['client_id']
   

    if request.POST['allow'] == "true":
        # if allowed, do following
        session = OAuthSession(app=OAuthApplication.objects.get(public_key=client_id),user=request.user)
        session.session_id = md5.new("%scr" % (datetime.datetime.now)).hexdigest()
        session.access_token = md5.new("%scr$access" % (datetime.datetime.now)).hexdigest()
        session.code = md5.new('%s$acess' % (datetime.datetime.now)).hexdigest()
        session.save()
        return HttpResponseRedirect('%s?code=%s' % (your_url,session.code))
    else:
        # Redirect to error page
        return HttpResponseRedirect('%s?error=access_denied&error_description=The+user+denied+your+request' % your_url)
    return HttpResponse("OK")
@csrf_exempt  
def api_find(request,version,access_token,object_type):
    return oauth_find(request,version,access_token,object_type)
@csrf_exempt  
def api_add_playlist(request,version,access_token):
    return add_playlist(request,version,access_token)
@csrf_exempt       
def api_me(request,version,access_token):
    return oauth_me(request,version,access_token)

@csrf_exempt
def api_playlists_regular(request,version,access_token,user):
    return oauth_playlists_regular(request,version,access_token)
@csrf_exempt
def api_gateway(request,access_token,version,object_type,object_id=-1,format="xml",function="get"):
    return gateway(request,access_token,version,object_type,object_id,format,function)