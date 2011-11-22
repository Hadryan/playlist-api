"""
 Copyright 2011 Alexander Foreselius

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
from django.utils.encoding import *
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest,HttpResponseRedirect
from django.template import RequestContext
from playlist_api.models import *
from django.db import models
from django.views.decorators.csrf import *       
from django.contrib.admin import *
from django.contrib import *
import md5
import json
import logging
import urllib
    
def access_token(request):
    client_id = request.GET['client_id']
    app_secret = request.GET['client_secret']
    _code = request.GET['code']
    redirect_uri = request.GET['redirect_uri']
    
    oauth_session = OAuthSession.objects.filter(code=_code)[0] # Get oauth_session
    if not oauth_session == None:
       # Return an key
       return HttpResponse('access_token=%s&expires=512' % (oauth_session.access_token))
 
  
    return HttpResponse('{ ' +\
        '"error": { ' + \
        '    "type": "OAuthException",' + \
        ' "message" :  "Error validating verification code."' +\
        '}}')
def oauth_is_authorized(_access_token):
    """ Checks if you're authorized """
    try:
        oauth_session = OAuthSession.objects.get(access_token=_access_token) # Get oauth_session
        return oauth_session
    except:
        try:
            return  OAuthSession.objects.get(access_token=_access_token)[0]
        except:
            pass
        return None
def oauth_get_user(_access_token):
    """ Gets the user who authorized the app """
    try:
        oauth_session = OAuthSession.objects.get(access_token=_access_token) # Get oauth_session
        return oauth_session.user
    except:
        return None
def oauth_get_app(_access_token):
    """ Gets the underlying app for the session """
    try:
        oauth_session = OAuthSession.objects.get(access_token=_access_token) # Get oauth_session
        return oauth_session.app
    except:
        return None
def get_post_as_string(request):
   byte_str = request.raw_post_data
   str = smart_unicode(byte_str)
   return strdef add_playlist(request,version,access_token):
    """ Adds an playlsit to the collection """
    try:
        request_user = oauth_get_user(access_token)
        current_app = oauth_get_app(access_token)
        # Create an new playlist
        _title = request.POST['title']
        _slug = _title.replace('%20','_').replace(' ','_')
        playlist = Playlist(title=_title,slug=_slug,user=request_user,app=current_app)
        playlist.save()
        return HttpResponse("OK")
    except Exception,e: 
        return HttpResponse(e)
def gateway(request,access_token,version,object_type,object_id=-1,format="xml",function="get",):
    """ API gateway 
The architecture  is based on the architecture provided by Spotify translated to mediachrome uri
in django

https://github.com/spotify/playlist-api
    """
    # Get format
    if 'format' in request.GET:
        format = request.GET['format']
    session_user = user=oauth_get_user(access_token)
    current_app = oauth_get_app(access_token)
    if not oauth_is_authorized(access_token):
        return render_to_response('mc/api_error.%s' %(format),{'message':'Not authorized'})
    if version == '1':
        if object_type == 'playlist':
               
            if function == 'get':
              
                
                playlist = Playlist.objects.get(slug=object_id)
                
                return render_to_response('mc/api.%s' %(format),{'playlist':playlist},context_instance=RequestContext(request))
       
           
            if function == 'move':
                # Move {count} tracks in playlist {id} from {src-index} to {dst-index}.
              
                src_index = request.GET['src-index']
                count =request.GET['count']
                dst_index = request.GET['dst-index']
                playlist = Playlist.objects.get(slug=object_id)
                
                if playlist.is_collaborative or playlist.user == session_user:
                    playlist.move_songs(src_index,dst_index,count)
                    playlist.save()
                    return HttpResponse("OK")
                # TODO Add action here
                return HttpResponse("Problem")
              
            if function == 'add':
                tracklist = get_post_as_string(request) # TODO Add uris here by {@format}
                    
                try:
                    index = -1
                    if 'index' in request.GET:
                        index = (request.GET['index'])
                    name = str(object_id)
                    playlist = Playlist.objects.get(slug=name)
                    playlist.insert(index,tracklist)
                    if(playlist.is_collaborative or playlist.user == request_user):
                        playlist.save()
                    else:
                        return HttpResponse("NOT AUTHORIZED")
                    return HttpResponse(playlist.entries)
                except Exception, e:
                    return HttpResponse(e) 
            if function == 'remove':
                # Remove {count} tracks from playlist {id} starting at {index}. [L25]
                index = request.GET['index']
                tracks = request.GET['count']
                playlist = Playlist(slug=name,user=session_user,app=oauth_get_app(access_token))
                if not playlist.user == oauth_get_user(access_token):
                    return HttpResponse("PROBLEM")
                else:
                    # TODO Add removal code here
                    return HttpResponse("OK")
        
            if function == 'annotation':
                text = get_post_as_string(request)
                playlist = Playlist.objects.get(slug=object_id)
                if playlist.user == session_user:
                    playlist.description = text
                    playlist.save()
                # TODO add annotation action here
                return HttpResponse("OK")
            if function == 'image':
                text = request.raw_data
                # TODO add image action here
                return HttpResponse("OK")
    
def oauth_me(request,version,access_token):
    """ Gets your account on oauth """
    format = 'xml'
    if 'format' in request.GET:
        format = request.GET['format']
    session_user =oauth_get_user(access_token)
    current_app = oauth_get_app(access_token)
    if not oauth_is_authorized(access_token):
        return render_to_response('mc/api_error.%s' %(format),{'message':'Not authorized'})
    playlists = Playlist.objects.filter(user=session_user)
    return render_to_response('mc/api_%s.xml'%(format),{'user':session_user,'playlists':playlists},context_instance=RequestContext(request))

#@csrf_exempt       
def oauth_playlists_regular(request,version,access_token,user_name=None):
    """ Renders an user page """
    format = 'xml'
    if 'format' in request.GET:
        format = request.GET['format']
    # Check if the request is authorized
    session_user = user=oauth_get_user(access_token)
    current_app = oauth_get_app(access_token)
    if not oauth_is_authorized(access_token) or slug == None:
        return render_to_response('mc/api_error.%s' %(format),{'message':'Not authorized'})
    
    _user = User.objects.get(username=user_name)
    
    playlists = Playlist.objects.filter(user=_user)
    visible_playlists = [ playlist for playlist in playlists if playlist.user == session_user or playlist.public]
    
    return render_to_response('mc/api.%s'%(format),{'user':_user,'playlists':visible_playlists},context_instance=RequestContext(request))

def oauth_find(request,version,access_token,object_type):
    """ Finds an entity """
    if not oauth_is_authorized(access_token):
        return render_to_response('mc/api_error.%s' %(format),{'message':'Not authorized'})
   
    query = request.GET['q'] # The query
    format = 'xml'
    if 'format' in request.GET:
        format = request.GET['format']
    # do find action here
    return render_to_response('mc/api.%s' % format,{},context_instance=RequestContext(request))
