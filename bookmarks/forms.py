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

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            raise forms.ValidationError("Enter both email and password.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid email or password.")

        user = authenticate(self.request, username=user.username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid email or password.")

        self.user = user
        return cleaned_data

    def get_user(self):
        return self.user

class SignupForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'you@company.com', 'class': 'oinp'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Min. 8 characters', 'class': 'oinp'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return password1

    def _generate_username(self, email):
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def save(self):
        email = self.cleaned_data['email']
        password1 = self.cleaned_data['password1']
        username = self._generate_username(email)
        user = User.objects.create_user(username=username, email=email, password=password1)
        return user