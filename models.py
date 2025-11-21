from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

# Import validators
from .validators import validate_release_date_within_6_months, validate_stars_half_step

#user models
class DottifyUser(models.Model):
    """
    Extends Django's User via a profile model.
    Users are admin-created only
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=800)

    def __str__(self):
        return self.display_name

# content models

class Album(models.Model):
    cover_image = models.ImageField(blank=True, null=True, default="no_cover.jpg")
    title = models.CharField(max_length=800)
    artist_name = models.CharField(max_length=800)
    artist_account = models.ForeignKey(DottifyUser, on_delete=models.SET_NULL, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=5, decimal_places=2,
                                       validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("999.99"))]
                                       )

    class Format(models.TextChoices):
        SNGL = "SNGL", _("Single")
        RMST = "RMST", _("Remaster")
        DLUX = "DLUX", _("Deluxe Edition")
        COMP = "COMP", _("Compilation")
        LIVE = "LIVE", _("Live Recording")
    format = models.CharField(max_length=4, choices=Format.choices, blank=True, null=True)

    release_date = models.DateField(validators=[validate_release_date_within_6_months])
    slug = models.SlugField(editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "artist_name", "format"],
                name="unique_album_title_artist_format",
            )
        ]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title or "")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=800)
    length = models.PositiveIntegerField(validators=[MinValueValidator(10)])
    position = models.PositiveIntegerField(null=True, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["title", "album"], name="unique_song_title_per_album"),
        ]
        ordering = ["position", "id"]

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if creating and self.position is None:
            last_pos = (
                Song.objects.filter(album=self.album)
                .order_by("-position")
                .values_list("position", flat=True)
                .first()
            )
            self.position = (last_pos or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        pos = f"{self.position}. " if self.position else ""
        return f"{pos}{self.title} ({self.length}s)"


class Playlist(models.Model):
    name = models.CharField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)
    songs = models.ManyToManyField(Song, blank=True)
    class Visibility(models.IntegerChoices):
        HIDDEN = 0, _("Hidden")
        UNLISTED = 1, _("Unlisted")
        PUBLIC = 2, _("Public")
    visibility = models.IntegerField(choices=Visibility.choices, default=Visibility.HIDDEN)
    owner = models.ForeignKey(DottifyUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (owner: {self.owner})"

class Rating(models.Model):
    stars = models.DecimalField(
        max_digits=2, decimal_places=1, validators=[validate_stars_half_step]
    )
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stars}★"


class Comment(models.Model):
    comment_text = models.CharField(max_length=800)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(DottifyUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.comment_text[:60] + ("…" if len(self.comment_text) > 60 else "")
