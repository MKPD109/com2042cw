# Any form helpers should go in this file.
from django import forms
from .models import Album, Song


class AlbumForm(forms.ModelForm):
    """Form for creating and editing albums."""

    class Meta:
        model = Album
        fields = ['cover_image', 'title', 'artist_name', 'retail_price', 'format', 'release_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'artist_name': forms.TextInput(attrs={'class': 'form-control'}),
            'retail_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'format': forms.Select(attrs={'class': 'form-select'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SongForm(forms.ModelForm):
    """Form for creating and editing songs."""

    class Meta:
        model = Song
        fields = ['title', 'length', 'album']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'min': '10'}),
            'album': forms.Select(attrs={'class': 'form-select'}),
        }
