from django import forms



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
