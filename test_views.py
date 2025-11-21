from django.test import TestCase
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Album, Song, Playlist, DottifyUser, Comment, Rating

class ViewTests(TestCase):
    ''' Run tests for the user-facing views (Sheets C and D). '''

    HTTP_ROUTE_FOUND = [200, 301, 302, 401, 403]

    def setUp(self):
        ''' Run the following before each test method. '''
        # Basic Setup
        a = Album.objects.create(
            title='Explosion!!!',
            format='SNGL',
            artist_name='Megumin',
            release_date='2025-01-01',
            retail_price='2.99',
        )

        s1 = Song.objects.create(title='Chunchunmaru', album=a, length=281)
        s2 = Song.objects.create(title='Bakuretsu Magic', album=a, length=540)

        u = User.objects.create_user('megumin', 'megume@example.com', 'pw123')
        dottify_user = DottifyUser.objects.create(
            user=u, display_name='explosion!!!'
        )

        p = Playlist.objects.create(name='degen', owner=dottify_user,
                                    visibility=2)

        # Sheet D Setup
        Comment.objects.create(
            comment_text='typeshit typeshit 67!',
            playlist=p,
            owner=dottify_user
        )

        # A recent rating
        Rating.objects.create(
            stars=Decimal('5.0'),
            album=a
            # created_at is auto_now_add
        )

        # An old rating
        old_rating = Rating.objects.create(
            stars=Decimal('1.0'),
            album=a
        )
        # Manually set the date to be old
        old_rating.created_at = timezone.now() - timedelta(days=70)
        old_rating.save()

        # Record IDs
        self.a_id = a.id
        self.s1_id = s1.id
        self.s2_id = s2.id
        self.p_id = p.id
        self.dottify_user_id = dottify_user.id
        self.dottify_user = dottify_user

    # --- Sheet C Tests ---

    def test_home_view_exists(self):
        # User is not logged in for this test
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Updated to match setUp data
        self.assertContains(response, 'degen')
        self.assertContains(response, 'Explosion!!!')

    def test_album_search_view_not_public(self):
        # We return 401 explicitly in our updated view
        response = self.client.get('/albums/search/?q=Christmas%20Hits')
        self.assertEqual(response.status_code, 401)

    def test_album_search_view_allows_logged_in_users(self):
        # Login with the user created in setUp ('megumin'), not 'annie'
        self.client.login(username='megumin', password='pw123')
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
        slug_should_be = slugify(self.dottify_user.display_name)
        response = self.client.get(f'/users/{self.dottify_user_id}/')
        self.assertRedirects(response, f'/users/{self.dottify_user_id}/{slug_should_be}/')

    def test_user_detail_view_exists_with_slug(self):
        slug_should_be = slugify(self.dottify_user.display_name)
        response = self.client.get(f'/users/{self.dottify_user_id}/{slug_should_be}/')
        self.assertTrue(response.status_code in self.HTTP_ROUTE_FOUND)

    def test_user_detail_view_redirects_with_wrong_slug(self):
        slug_should_be = slugify(self.dottify_user.display_name)
        response = self.client.get(f'/users/{self.dottify_user_id}/this-slug-is-wrong/')
        self.assertRedirects(response, f'/users/{self.dottify_user_id}/{slug_should_be}/')

    # --- Sheet D Tests ---

    def test_total_results_on_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total results found: 1')

    def test_album_ratings_on_detail_page(self):
        response = self.client.get(f'/albums/{self.a_id}/')
        self.assertEqual(response.status_code, 200)
        # All time average (5.0 + 1.0) / 2 = 3.0
        self.assertContains(response, 'Average rating of all time: 3.0')
        # Recent average (only the 5.0 rating)
        self.assertContains(response, 'Recent rating average (last 60 days): 5.0')

    def test_playlist_comments_on_detail_page(self):
        response = self.client.get(f'/playlists/{self.p_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'typeshit typeshit 67!')
        self.assertContains(response, 'explosion!!!')

    # --- Edge Case Tests (Add these to the bottom of ViewTests class) ---

    def test_album_search_no_results(self):
        # Login with the user created in setUp
        self.client.login(username='megumin', password='pw123')
        response = self.client.get('/albums/search/?q=AquaUselessGoddess')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Explosion!!!')
        self.assertContains(response, 'Total results found: 0')

    def test_404_for_non_existent_album(self):
        response = self.client.get('/albums/99999/')
        self.assertEqual(response.status_code, 404)

    def test_delete_permission_denied_for_non_owner(self):
        u2 = User.objects.create_user('kazuma', 'kazuma@example.com', 'pw123')
        DottifyUser.objects.create(user=u2, display_name='Kazuma')
        self.client.login(username='kazuma', password='pw123')
        response = self.client.post(f'/albums/{self.a_id}/delete/')
        self.assertEqual(response.status_code, 403)
