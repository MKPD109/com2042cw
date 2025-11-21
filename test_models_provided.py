# Note that tests for Comment and Rating are not provided as these will
# user later. However, we will import these names to ensure they exist
# and are spelt correctly.

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Album, Song, Playlist, Comment, Rating, DottifyUser


class ProvidedTestSheetA(TestCase):
    def test_can_create_album(self):
        a = Album(
            title='Greatest Hits',
            format='SNGL',
            artist_name='Johnny Singer',
            release_date='2025-01-01',
            retail_price='2.99',
        )

        a.full_clean()
        a.save()

        assert Album.objects.filter(title='Greatest Hits').count() == 1
        a.delete()

    def test_can_create_song(self):
        a = Album.objects.create(
            title='Greatest Hits',
            artist_name='Johnny Singer',
            release_date='2025-01-01',
            retail_price='2.99',
        )

        s = Song(title='One Hit Wonder', album=a, length=281)

        s.full_clean()
        s.save()

        assert Song.objects.filter(title='One Hit Wonder').count() == 1
        s.delete()

    def test_can_create_dottify_user(self):
        u = User.objects.create_user('annie', 'an@example.com', 'pw123')
        dottify_user = DottifyUser(user=u, display_name='AnnieMusicLover92')
        dottify_user.full_clean()
        dottify_user.save()

        users = DottifyUser.objects.filter(display_name__contains='MusicLover')
        assert users.count() == 1
        dottify_user.delete()
        u.delete()

    def test_can_create_playlist(self):
        u = User.objects.create_user('annie', 'an@example.com', 'pw123')
        dottify_user = DottifyUser.objects.create(
            user=u, display_name='AnnieMusicLover92'
        )

        p = Playlist(name='Work Jams 2', owner=dottify_user)
        p.full_clean()
        p.save()

        assert dottify_user.playlist_set.all().count() == 1
        p.delete()
        dottify_user.delete()
        u.delete()
