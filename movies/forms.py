from django import forms
from .models import Rating


class RatingForm(forms.ModelForm):
    """Form for submitting movie ratings and reviews"""
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rate from 1 to 10'
        }),
        help_text='Select a rating between 1 and 10'
    )
    
    review = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your review here (optional)...'
        }),
        help_text='Share your thoughts about this movie'
    )
    
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        
    def clean_rating(self):
        """Ensure rating is within valid range"""
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 10:
            raise forms.ValidationError('Rating must be between 1 and 10.')
        return rating
    
    def clean_review(self):
        """Validate review length"""
        review = self.cleaned_data.get('review')
        if review and len(review) > 1000:
            raise forms.ValidationError('Review must be less than 1000 characters.')
        return review


class SearchForm(forms.Form):
    """Form for advanced movie search"""
    
    q = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Search movies...'
        }),
        label='Search'
    )
    
    def clean_q(self):
        """Sanitize search query"""
        query = self.cleaned_data.get('q')
        if query:
            # Remove extra whitespace
            query = ' '.join(query.split())
        return query
