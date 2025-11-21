# Write your API serialisers here.
from rest_framework import serializers
from .models import Album, Song, Playlist, DottifyUser


class AlbumSerializer(serializers.ModelSerializer):
    """
    Serializer for Album model.
    - artist_account is excluded (not visible or settable via API)
    - song_set shows song titles as strings
    """
    song_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = [
            'id',
            'cover_image',
            'title',
            'artist_name',
            'retail_price',
            'format',
            'release_date',
            'slug',
            'song_set'
        ]
        read_only_fields = ['slug', 'song_set']


class SongSerializer(serializers.ModelSerializer):
    """
    Serializer for Song model.
    - position is excluded (not visible or settable via API)
    - album is given as an ID
    """
    class Meta:
        model = Song
        fields = ['id', 'title', 'length', 'album']


class PlaylistSerializer(serializers.ModelSerializer):
    """
    Serializer for Playlist model (read-only).
    - owner is returned as their display_name
    - songs are listed as hyperlinks (REST Level 3)
    """
    owner = serializers.CharField(source='owner.display_name', read_only=True)
    songs = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='song-detail'
    )

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'created_at', 'visibility', 'owner', 'songs']
        read_only_fields = ['id', 'name', 'created_at', 'visibility', 'owner', 'songs']
