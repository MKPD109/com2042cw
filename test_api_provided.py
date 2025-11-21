# You can also use Django's base TestCase (which in turn uses unittest),
# but you would need to set the format to JSON for everything.
from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth.models import User
from .models import Album, Song, Playlist, DottifyUser


class ProvidedTestSheetB(APITestCase):
    ''' Run tests for the API. Uses Django's ephemeral test database. '''

    song_keys = ['title', 'length', 'album']
    playlist_keys = ['songs', 'owner', 'name', 'created_at']

    album_keys = ['cover_image', 'title', 'artist_name', 'retail_price',
                  'format', 'release_date', 'song_set']
    stats_keys = ['playlist_count', 'user_count', 'album_count',
                  'song_length_average']

    def setUp(self):
        ''' Run the following before each test method. '''
        a = Album.objects.create(
            title='Greatest Hits',
            format='SNGL',
            artist_name='Johnny Singer',
            release_date='2025-01-01',
            retail_price='2.99',
        )

        s1 = Song.objects.create(title='One Hit Wonder', album=a, length=281)
        s2 = Song.objects.create(title='Another Bop', album=a, length=540)

        u = User.objects.create_user('annie', 'an@example.com', 'pw123')
        dottify_user = DottifyUser.objects.create(
            user=u, display_name='AnnieMusicLover92'
        )

        p = Playlist.objects.create(name='Work Jams 2', owner=dottify_user,
                                    visibility=2)

        # Record IDs for the tests, so we can reference these objects.
        self.a_id = a.id
        self.s1_id = s1.id
        self.s2_id = s2.id
        self.p_id = p.id
        self.dottify_user_id = dottify_user.id


    def tearDown(self):
        ''' Tidy up after each test method. '''

        # THINK: Why MUST we be doing this against a TEST database?!!!
        # Also: why should we remove the test objects after each test
        # or test suite? (Hint: think reproducibility)
        Song.objects.all().delete()
        Album.objects.all().delete()
        Playlist.objects.all().delete()
        DottifyUser.objects.all().delete()
        User.objects.all().delete()

    def test_album_list_api_view_exists(self):
        response = self.client.get('/api/albums/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json()[0] for k in self.album_keys))
        self.assertTrue(response.json()[0]['title'] == 'Greatest Hits')

    def test_album_detail_api_view_exists(self):
        response = self.client.get(f'/api/albums/{self.a_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json() for k in self.album_keys))
        self.assertTrue(response.json()['title'] == 'Greatest Hits')

    def test_song_list_api_view_exists(self):
        response = self.client.get('/api/songs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json()[0] for k in self.song_keys))
        self.assertTrue(response.json()[0]['title'] == 'One Hit Wonder')

    def test_song_detail_api_view_exists(self):
        response = self.client.get(f'/api/songs/{self.s1_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json() for k in self.song_keys))
        self.assertTrue(response.json()['title'] == 'One Hit Wonder')

    def test_playlist_list_api_view_exists(self):
        response = self.client.get('/api/playlists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json()[0] for k in self.playlist_keys))
        self.assertTrue(response.json()[0]['name'] == 'Work Jams 2')

    def test_playlist_detail_api_view_exists(self):
        response = self.client.get(f'/api/playlists/{self.p_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json() for k in self.playlist_keys))
        self.assertTrue(response.json()['name'] == 'Work Jams 2')

    def test_album_song_list_api_view_exists(self):
        response = self.client.get(f'/api/albums/{self.a_id}/songs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json()[0] for k in self.song_keys))
        self.assertTrue(response.json()[0]['title'] == 'One Hit Wonder')

    def test_album_song_detail_api_view_exists(self):
        response = self.client.get(f'/api/albums/{self.a_id}/songs/{self.s1_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(k in response.json() for k in self.song_keys))
        self.assertTrue(response.json()['title'] == 'One Hit Wonder')

    def test_statistics_api_view_exists(self):
        response = self.client.get(f'/api/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
