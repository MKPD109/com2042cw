# Use this file for your API viewsets only
# E.g., from rest_framework import ...
from django.db.models import Avg
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Album, Song, Playlist, DottifyUser
from .serializers import AlbumSerializer, SongSerializer, PlaylistSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Album CRUD operations.
    Supports list, create, retrieve, update, and delete.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class SongViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Song CRUD operations.
    Supports list, create, retrieve, update, and delete.
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer


class PlaylistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Playlist.
    Only returns public playlists (visibility = 2).
    """
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        # Only return public playlists
        return Playlist.objects.filter(visibility=Playlist.Visibility.PUBLIC)


class NestedSongViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only nested ViewSet for Songs under a specific Album.
    Routes: /api/albums/[album_id]/songs/ and /api/albums/[album_id]/songs/[song_id]/
    """
    serializer_class = SongSerializer

    def get_queryset(self):
        # Get the album_pk from the URL
        album_pk = self.kwargs.get('album_pk')
        # Return songs filtered by album
        return Song.objects.filter(album_id=album_pk)

    def retrieve(self, request, pk=None, album_pk=None):
        """
        Get a specific song under an album.
        Returns 404 if the song doesn't belong to the album.
        """
        # Get the song and verify it belongs to the album
        song = get_object_or_404(Song, pk=pk, album_id=album_pk)
        serializer = self.get_serializer(song)
        return Response(serializer.data)


class StatisticsAPIView(APIView):
    """
    API view for statistics endpoint.
    Returns counts and averages for various models.
    """
    def get(self, request):
        # Count users
        user_count = DottifyUser.objects.count()

        # Count albums
        album_count = Album.objects.count()

        # Count public playlists
        playlist_count = Playlist.objects.filter(
            visibility=Playlist.Visibility.PUBLIC
        ).count()

        # Calculate average song length
        # Returns None if no songs exist, so default to 0
        song_length_avg = Song.objects.aggregate(
            avg_length=Avg('length')
        )['avg_length']

        # Handle case where there are no songs
        song_length_average = float(song_length_avg) if song_length_avg is not None else 0.0

        return Response({
            'user_count': user_count,
            'album_count': album_count,
            'playlist_count': playlist_count,
            'song_length_average': song_length_average
        })
