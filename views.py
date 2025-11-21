# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Q, Avg
from django.template.defaultfilters import slugify
from django.utils import timezone
from datetime import timedelta

from .forms import AlbumForm, SongForm
from .models import Album, Song, Playlist, DottifyUser, Comment, Rating



class HomeView(ListView):
    """
    Home page view - displays different content based on user authentication and group.

    Rules:
    - Not logged in: Show all albums and public playlists
    - Logged in (no group): Show user's own playlists only
    - Artist group: Show only their own albums (via artist_account)
    - DottifyAdmin group: Show all albums, songs, and playlists
    """
    template_name = 'dottify/home.html'
    context_object_name = 'albums'

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            # Not logged in: show all albums
            return Album.objects.all()

        # Check if user is in DottifyAdmin group
        if user.groups.filter(name='DottifyAdmin').exists():
            # Admin sees all albums
            return Album.objects.all()

        # Check if user is in Artist group
        if user.groups.filter(name='Artist').exists():
            # Artist sees only their own albums
            try:
                dottify_user = DottifyUser.objects.get(user=user)
                return Album.objects.filter(artist_account=dottify_user)
            except DottifyUser.DoesNotExist:
                return Album.objects.none()

        # Regular logged-in user: no albums shown
        return Album.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Get the count from the queryset for albums
        context['total_results'] = context['albums'].count()

        # Handle playlists
        if not user.is_authenticated:
            # Not logged in: show public playlists
            context['playlists'] = Playlist.objects.filter(visibility=Playlist.Visibility.PUBLIC)
        elif user.groups.filter(name='DottifyAdmin').exists():
            # Admin sees all playlists
            context['playlists'] = Playlist.objects.all()
        else:
            # Logged-in user: show only their own playlists
            try:
                dottify_user = DottifyUser.objects.get(user=user)
                context['playlists'] = Playlist.objects.filter(owner=dottify_user)
            except DottifyUser.DoesNotExist:
                context['playlists'] = Playlist.objects.none()

        # Handle songs (only for DottifyAdmin)
        if user.is_authenticated and user.groups.filter(name='DottifyAdmin').exists():
            context['songs'] = Song.objects.all()

        return context



def album_search(request):
    """
    Search albums by title (case-insensitive).
    User must be logged in.
    """
    if not request.user.is_authenticated:
        return HttpResponse("You must be logged in to view this page.", status=401)
    query = request.GET.get('q', '')
    albums = Album.objects.filter(title__icontains=query) if query else Album.objects.none()
    total_results = albums.count()

    return render(request, 'dottify/album_search.html', {
        'albums': albums,
        'query': query,
        'total_results': total_results
    })


class AlbumDetailView(DetailView):
    """
    Display album details with songs.
    Accessible to everyone (no login required).
    """
    model = Album
    template_name = 'dottify/album_detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['songs'] = self.object.song_set.all()
        all_time_avg = self.object.rating_set.aggregate(Avg('stars'))['stars__avg'] or 0.0

        # Calculate recent average rating (last 60 days)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        recent_avg = self.object.rating_set.filter(created_at__gte=sixty_days_ago).aggregate(Avg('stars'))['stars__avg'] or 0.0

        # Add formatted strings to context
        context['all_time_rating'] = f"Average rating of all time: {all_time_avg:.1f}"
        context['recent_rating'] = f"Recent rating average (last 60 days): {recent_avg:.1f}"
        return context


class IsArtistOrAdminMixin(UserPassesTestMixin):
    """Mixin to check if user is in Artist or DottifyAdmin group."""

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=['Artist', 'DottifyAdmin']).exists()


class AlbumCreateView(LoginRequiredMixin, IsArtistOrAdminMixin, CreateView):
    """
    Create a new album.
    User must be logged in and in Artist or DottifyAdmin group.
    """
    model = Album
    form_class = AlbumForm
    template_name = 'dottify/album_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, f'Album "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an album.
    User must be logged in and in Artist or DottifyAdmin group.
    If Artist, must own the album via artist_account.
    """
    model = Album
    form_class = AlbumForm
    template_name = 'dottify/album_form.html'

    def get_success_url(self):
        return reverse('album-detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        album = self.get_object()
        user = self.request.user

        # Check if user is admin
        if user.groups.filter(name='DottifyAdmin').exists():
            return True

        # Check if user is artist and owns the album
        if user.groups.filter(name='Artist').exists():
            try:
                dottify_user = DottifyUser.objects.get(user=user)
                if album.artist_account == dottify_user:
                    return True
            except DottifyUser.DoesNotExist:
                pass

        return False

    def form_valid(self, form):
        messages.success(self.request, f'Album "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class AlbumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an album.
    User must be logged in and either:
    - In DottifyAdmin group, OR
    - Be the album's artist (via artist_account)
    """
    model = Album
    template_name = 'dottify/album_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        album = self.get_object()
        user = self.request.user

        # Check if user is admin
        if user.groups.filter(name='DottifyAdmin').exists():
            return True

        # Check if user is the album's artist
        try:
            dottify_user = DottifyUser.objects.get(user=user)
            if album.artist_account == dottify_user:
                return True
        except DottifyUser.DoesNotExist:
            pass

        return False

    def form_valid(self, form):
        messages.success(self.request, f'Album "{self.object.title}" deleted successfully!')
        return super().form_valid(form)


class SongDetailView(DetailView):
    """Display song details with parent album link."""
    model = Song
    template_name = 'dottify/song_detail.html'
    context_object_name = 'song'


class SongCreateView(LoginRequiredMixin, IsArtistOrAdminMixin, CreateView):
    """
    Create a new song.
    User must be logged in and in Artist or DottifyAdmin group.
    If Artist, must own the selected album.
    """
    model = Song
    form_class = SongForm
    template_name = 'dottify/song_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = self.request.user
        album = form.cleaned_data['album']

        # If user is Artist, check they own the album
        if user.groups.filter(name='Artist').exists():
            try:
                dottify_user = DottifyUser.objects.get(user=user)
                if album.artist_account != dottify_user:
                    return HttpResponseForbidden("You can only add songs to your own albums.")
            except DottifyUser.DoesNotExist:
                return HttpResponseForbidden("You don't have a Dottify user account.")

        messages.success(self.request, f'Song "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class SongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update a song.
    User must be logged in and either:
    - In DottifyAdmin group, OR
    - Be the song's album's artist
    """
    model = Song
    form_class = SongForm
    template_name = 'dottify/song_form.html'

    def get_success_url(self):
        return reverse('song-detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        song = self.get_object()
        user = self.request.user

        # Check if user is admin
        if user.groups.filter(name='DottifyAdmin').exists():
            return True

        # Check if user is the song's album's artist
        try:
            dottify_user = DottifyUser.objects.get(user=user)
            if song.album.artist_account == dottify_user:
                return True
        except DottifyUser.DoesNotExist:
            pass

        return False

    def form_valid(self, form):
        messages.success(self.request, f'Song "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a song.
    User must be logged in and either:
    - In DottifyAdmin group, OR
    - Be the song's album's artist
    """
    model = Song
    template_name = 'dottify/song_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        song = self.get_object()
        user = self.request.user

        # Check if user is admin
        if user.groups.filter(name='DottifyAdmin').exists():
            return True

        # Check if user is the song's album's artist
        try:
            dottify_user = DottifyUser.objects.get(user=user)
            if song.album.artist_account == dottify_user:
                return True
        except DottifyUser.DoesNotExist:
            pass

        return False

    def form_valid(self, form):
        messages.success(self.request, f'Song "{self.object.title}" deleted successfully!')
        return super().form_valid(form)


def user_detail(request, pk, slug=None):
    """
    Display DottifyUser details with playlists.
    Handles slug validation and redirects to canonical URL if needed.
    """
    dottify_user = get_object_or_404(DottifyUser, pk=pk)
    correct_slug = slugify(dottify_user.display_name)

    # If slug is missing or incorrect, redirect to canonical URL
    if slug != correct_slug:
        return redirect('user-detail-slug', pk=pk, slug=correct_slug)

    # Get user's playlists
    playlists = Playlist.objects.filter(owner=dottify_user)

    return render(request, 'dottify/user_detail.html', {
        'dottify_user': dottify_user,
        'playlists': playlists
    })

class PlaylistDetailView(DetailView):
    """
    Display Playlist details with comments.
    """
    model = Playlist
    template_name = 'dottify/playlist_detail.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all comments for this playlist, pre-fetching the owner's display_name
        context['comments'] = self.get_object().comment_set.select_related('owner').all()
        return context
