# You can also use Django's base TestCase (which in turn uses unittest),
# but you would need to set the format to JSON for everything.
from django.test import TestCase

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from .models import Album, Song, Playlist, DottifyUser


class ProvidedTestSheetC(TestCase):
    ''' Run tests for the user-facing views. Just checks they exist. '''

    # Most of these tests look to see if routes exist, not their content
    # nor authorisation (Sheet D) -- you need to do this according to
    # Sheet C and D.
    HTTP_ROUTE_FOUND = [200, 301, 302, 401, 403]

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

    def test_home_view_exists(self):
        # User is not logged in for this test, so it should list albums
        # and public playlists.
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work Jams 2')
        self.assertContains(response, 'Greatest Hits')

    def test_album_search_view_not_public(self):
        response = self.client.get('/albums/search/?q=Christmas%20Hits')
        self.assertEqual(response.status_code, 401)

    # We will NOT provide any further tests for authentication -- you will need
    # to do this as the test component of Sheet D. Further tests will only
    # check your URL configuration. You should check the content of your views.
    def test_album_search_view_allows_logged_in_users(self):
        self.client.login(username='annie', password='pw123')
        response = self.client.get('/albums/search/?q=Christmas%20Hits')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_album_create_view_exists(self):
        response = self.client.get('/albums/new/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_album_read_view_exists_via_id(self):
        response = self.client.get(f'/albums/{self.a_id}/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_album_read_view_exists_via_id_slug(self):
        slug_should_be = slugify(Album.objects.get(id=self.a_id).title)
        response = self.client.get(f'/albums/{self.a_id}/{slug_should_be}/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    # Recall from Week 3: routing and usability are important. Slugs probably
    # aren't great for routing on their own. The use of an ID and slug means:
    # - Routes are readable (SEO, usability)
    # - Entity titles are updateable, with links updatable without breaking
    # - Spelling mistakes in the slug (from the user) don't impact routing
    # - Routes do not break, even if slugs are updated
    # We therefore use the ID to look up entities, not the slug. IDs are
    # unchanging.
    def test_album_read_view_exists_via_any_slug(self):
        response = self.client.get(f'/albums/{self.a_id}/any-slug-is-fine/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_album_edit_view_exists(self):
        response = self.client.get(f'/albums/{self.a_id}/edit/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_album_delete_view_exists(self):
        response = self.client.get(f'/albums/{self.a_id}/delete/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_song_create_view_exists(self):
        response = self.client.get('/songs/new/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_song_read_view_exists(self):
        response = self.client.get(f'/songs/{self.s1_id}/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_song_edit_view_exists(self):
        response = self.client.get(f'/songs/{self.s1_id}/edit/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_song_delete_view_exists(self):
        response = self.client.get(f'/songs/{self.s1_id}/delete/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_user_detail_view_exists(self):
        slug_should_be = slugify(
            DottifyUser.objects.get(id=self.dottify_user_id).display_name)

        response = self.client.get(f'/users/{self.dottify_user_id}/')

        self.assertRedirects(response,
                             f'/users/{self.dottify_user_id}/{slug_should_be}/')

    def test_user_detail_view_exists_with_slug(self):
        slug_should_be = slugify(
            DottifyUser.objects.get(id=self.dottify_user_id).display_name)

        response = self.client.get(f'/users/{self.dottify_user_id}/{slug_should_be}/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_user_detail_view_redirects_with_wrong_slug(self):
        slug_should_be = slugify(
            DottifyUser.objects.get(id=self.dottify_user_id).display_name)

        response = self.client.get(
            f'/users/{self.dottify_user_id}/this-slug-is-wrong/')

        self.assertRedirects(response,
                             f'/users/{self.dottify_user_id}/{slug_should_be}/')
