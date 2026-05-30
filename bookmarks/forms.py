from django import forms

class BookmarkForm(forms.Form):

    url = forms.URLField(
        label="Article URL"
    )