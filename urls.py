from django.urls import path, include
from rest_framework_nested import routers

from .api_views import (
    AlbumViewSet,
    SongViewSet,
    PlaylistViewSet,
    NestedSongViewSet,
    StatisticsAPIView
)

# Create the main router
router = routers.DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'songs', SongViewSet, basename='song')
router.register(r'playlists', PlaylistViewSet, basename='playlist')

# Create nested router for album songs
albums_router = routers.NestedDefaultRouter(router, r'albums', lookup='album')
albums_router.register(r'songs', NestedSongViewSet, basename='album-songs')

from .views import (
    HomeView, album_search, AlbumDetailView, AlbumCreateView,
    AlbumUpdateView, AlbumDeleteView, SongDetailView, SongCreateView,
    SongUpdateView, SongDeleteView, user_detail, PlaylistDetailView
)

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    path('api/', include(albums_router.urls)),
    path('api/statistics/', StatisticsAPIView.as_view(), name='statistics'),

    # HTML view routes
    # Home
    path('', HomeView.as_view(), name='home'),

    # Album routes
    path('albums/search/', album_search, name='album-search'),
    path('albums/new/', AlbumCreateView.as_view(), name='album-create'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album-detail'),
    path('albums/<int:pk>/edit/', AlbumUpdateView.as_view(), name='album-edit'),
    path('albums/<int:pk>/delete/', AlbumDeleteView.as_view(), name='album-delete'),
    path('albums/<int:pk>/<slug:slug>/', AlbumDetailView.as_view(), name='album-detail-slug'),

    # Song routes
    path('songs/new/', SongCreateView.as_view(), name='song-create'),
    path('songs/<int:pk>/', SongDetailView.as_view(), name='song-detail'),
    path('songs/<int:pk>/edit/', SongUpdateView.as_view(), name='song-edit'),
    path('songs/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),

    # Playlist routes
    path('playlists/<int:pk>/', PlaylistDetailView.as_view(), name='playlist-detail'),

    # User routes
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/<int:pk>/<slug:slug>/', user_detail, name='user-detail-slug'),
]
