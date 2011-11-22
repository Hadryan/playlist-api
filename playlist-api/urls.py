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
   
from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('',
    (r'^$','myproject.mediachrome.views.index'),
    (r'^playlist/(?P<slug>\w+)/$','myproject.mediachrome.views.playlist'),
    (r'^oauth/$','myproject.mediachrome.views.oauth'),
    (r'^oauth/do','myproject.mediachrome.views.oauth_do'),
	(r'^tose/$','myproject.mediachrome.views.terms_of_conditions'),
	(r'^login/$','myproject.mediachrome.views.login_view'),
    (r'^oauth/access_token','myproject.mediachrome.views.access_token'),
    (r'^spotify/app/(?P<app>\w+)/(?P<par>\w+)/$','myproject.mediachrome.views.spotifyapps'),
    (r'^channel/add/$','myproject.mediachrome.views.channel_form'),
    (r'^channel/all/$','myproject.mediachrome.views.channel_list'),
    (r'^channel/add/do/$','myproject.mediachrome.views.add_channel_do'),
    
    (r'^login/do$','myproject.mediachrome.views.login_do'),
    (r'^logout/$','myproject.mediachrome.views.logout_do'),
    (r'^apps/add/$','myproject.mediachrome.views.add_app_view'),
    (r'^apps/add/do/$','myproject.mediachrome.views.add_app_do'),
	(r'^apps/help/$','myproject.mediachrome.views.oauth_help'),
	(r'^apps/help/content/$','myproject.mediachrome.views.oauth_help_content'),
    (r'^(?P<user_name>\w+)/channel/(?P<id>\w+)/$','myproject.mediachrome.views.channel'),
	(r'^apps/help/auth/$','myproject.mediachrome.views.oauth_help_auth'),
    (r'^signup/$','myproject.mediachrome.views.signup'),
    (r'^signup/do/$','myproject.mediachrome.views.signup_do'),
    (r'^apps/$','myproject.mediachrome.views.apps_view'),
    (r'^apps/(?P<app_id>\w+)/details/$','myproject.mediachrome.views.app_detail_view'),
    (r'^apps/(?P<app_id>\w+)/log/$','myproject.mediachrome.views.app_log_view'),
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/me/$','myproject.mediachrome.views.api_me'),
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/user/(?P<user_name>\w+)/playlists/regular.(?P<format>\w+)$','myproject.mediachrome.views.api_playlists_regular'),
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/playlist.(?P<format>\w+)$','myproject.mediachrome.views.api_add_playlist'),
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/find/(?P<object_type>\w+)$','myproject.mediachrome.views.api_find'),
    (r'^import/$','myproject.mediachrome.views.content_import'),
    
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/(?P<object_type>\w+)/(?P<object_id>\w+)/$','myproject.mediachrome.views.api_gateway'),
    (r'^api/(?P<version>\w+)/(?P<access_token>\w+)/(?P<object_type>\w+)/(?P<object_id>\w+)/(?P<function>\w+)/$','myproject.mediachrome.views.api_gateway'),
   
   
)