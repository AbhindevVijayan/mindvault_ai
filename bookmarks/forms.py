from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class BookmarkForm(forms.Form):

    url = forms.URLField(
        label="Article URL"
    )

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'you@company.com', 'class': 'oinp'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********', 'class': 'oinp'}))
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data