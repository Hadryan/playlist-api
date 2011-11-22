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
from xml.dom.minidom import *
from xml.dom import minidom
from django.db import models
from django.contrib.auth.models import *
from datetime import *
from pyexpat import *
import urllib2
from xml.dom.minidom import parse   
from urllib import *
OAUTH_EVENT_TYPE = (
    (u'ADD_PLAYLIST','Add playlist'),
    (u'RM_PLAYLIST','Remove playlist'),
)
OAUTH_OBJECT_TYPE = (
    (u'PLAYLIST','Playlist'),
    (u'USER','User')
)

class OAuthApplication(models.Model):
    """ An oauth application to the system """
    name = models.CharField(max_length=200)
    secret_key = models.CharField(max_length=256)
    public_key = models.CharField(max_length=256)
    # date_created = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User)
    description= models.TextField()                             # App description
    def __unicode__(self):
        """ Returns the name of the app """
        return self.name
class OAuthSession(models.Model):
    """ An oauth session """
    app = models.ForeignKey(OAuthApplication)
    expire_date = models.DateTimeField(default=datetime.now)
    creation_date = models.DateTimeField(default=datetime.now)
    session_id = models.CharField(max_length=256)
    access_token = models.CharField(max_length=256)
    code = models.CharField(max_length=256,null=True,blank=True,default='')
    user = models.ForeignKey(User)
class OAuthEvent(models.Model):
    """ An event logged in an specific oauth session """
    oauth_session = models.ForeignKey(OAuthSession)
    app = models.ForeignKey(OAuthApplication,default=None,null=True)
    time = models.DateTimeField(default=datetime.now)
    type = models.CharField(max_length=10,choices=OAUTH_EVENT_TYPE,default=u'ADD_PLAYLIST')
    object_id = models.PositiveIntegerField() # Object id
    object_type = models.CharField(max_length=10,choices=OAUTH_OBJECT_TYPE)
    
    def __unicode__(self):
        return "%s" % self.type
class Song(models.Model):
    uri = models.CharField(max_length=256)
    def __init__(self,uri):
        super(Song,self).__init__()
        """ Parse an song from URI 
        # song://<domain>/<artist>/<album>/<title>[/<version>] ->
        # song:<domain>:<artist>:<album>:<title>:<version>"""
        self.uri = uri
        a = uri.replace('//','/')
        a = uri.replace('/',':')
        a = a.replace(':::',':')
       
        tokens = a.split(':')
        if len(tokens) > 2:
           _title = urllib.unquote_plus(tokens[4])
           _artist = urllib.unquote_plus(tokens[2])
           _album = urllib.unquote_plus(tokens[3])
         
           _version = tokens[4]
           self.artist=_artist
           self.album=_album 
           self.version=_version
           self.title=_title
          
        else:
            if len(tokens) == 2:
               _isrc = tokens[1]
               
            else:
                pass
    uri = models.CharField(max_length=500)
    isrc = models.CharField(max_length=12)
    title = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    starred = models.BooleanField()
    user = models.ForeignKey(User)
    def href(self):
        uri = "song://%s/%s/%s/%s/%s/" % ('mediachrome',self.artist,self.album,self.title,self.version)
        return uri
    
    def __unicode_(self):
        return "%s - %s" % (self.artist, self.title)
class Playlist(models.Model):
    """ An playlist """
    app = models.ForeignKey(OAuthApplication,blank=True,null=True)
    entries = models.TextField()                                # Entries
    user = models.ForeignKey(User)                              # User of playlist
    popularity = models.FloatField(default=0.0)                 # Popularity
    title = models.CharField(max_length=200)                    # Title
    slug = models.SlugField(default='')
    annotation = models.TextField()                             # Text of playlist
    picture = models.URLField()                                 # Picture of playlist
    creation_date = models.DateTimeField(default=datetime.now)
    public = models.BooleanField()
    def insert(self,index,tracklist):
        # if entries is empty, just add them
        if self.entries == '':
            self.entries = tracklist
            return
        # Otherwise parse it
        index = int(str(index))
        
        """ Inserts an song to the playlist """
        c = self.entries.split('\n') # split entries into different parts
        new_entries = ""
        for entry in tracklist.split("\n"):
            new_entries+='\n' + entry
        # index is -1 append the entries to the end of the list
        if index == -1:
            self.entries += '\n' + tracklist
            return
        # Otherwise append it at desired position
        self.entries = self.entries[:unicode.index(self.entries,(c[index-1]))] + '\n' +  new_entries + '\n' + self.entries[unicode.index(self.entries,(c[index-1])): ].replace('\n\n','\n') 
        
  
    def is_collaborative(self):
        return False
    def move_songs(self,old_index,new_index,length):
        """ Move songs on the playlist """
        c = self.entries.split('\n')
        old_index = int(old_index)
        new_index = int(new_index)
        length = int(length)
        length = new_index-old_index
        indices = c[old_index:old_index+length+1]
        del c[old_index:old_index+length]
        # Append items to the list -------------------------------
        i=0
        for item in indices:
            c.insert(new_index+i,item)
        # Make string --------------------------------------------
        str = ""
        for entry in c:
            str+=entry
        self.entries = str
        
    def delete_songs(self,start_index,length):
        """ Delete the bunch of songs from the list """
        c = self.entries.split('\n')
        start_index = int(start_index)
        length = int(length)
        del c[start_index:length]
        str = ""
        for entry in c:
            str+=entry
        self.entries = str
    def songs(self):
        """ Get songs """
     
        songs = []
        c = self.entries.splitlines(False)   # Splits entries by newline
        
        for str in c:
            if not str == '':
                song = Song(str)
                songs.append(song)
        return songs
    def __unicode__(self):
        return self.title
class PlaylistState(models.Model):
    """ An certain state of playlist """
    entries = models.TextField()                                    # Entries
    user = models.ForeignKey(User) 
    time = models.DateTimeField(default=datetime.now)               # c 
    playlist = models.ForeignKey(Playlist)
    
class Comment(models.Model):
    """ Comment to playlist """
    playlist = models.ForeignKey(Playlist)
    user = models.ForeignKey(User)
    text = models.TextField()
    
class Attribute(models.Model):
    """ An certain attribute """
    name = models.CharField(max_length=100)
    verbose_name = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.name
    
class Property(models.Model):
    """ An instance of the attribute assigned to an certain playlist """
    attribute = models.ForeignKey(Attribute) 
    value = models.CharField(max_length=500)
    playlist = models.ForeignKey(Playlist)

class Tag(models.Model):
    name = models.CharField(max_length=500)
    user = models.ForeignKey(User)
    playlist = models.ManyToManyField(Playlist)
    