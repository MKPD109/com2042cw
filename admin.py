from django.contrib import admin
from .models import DottifyUser, Album, Song, Playlist, Rating, Comment

admin.site.register([DottifyUser, Album, Song, Playlist, Rating, Comment])
