from django import forms
from django.contrib.auth.models import User

from Connectly.models import Post, Profile
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['media_file', 'body']
        widgets = {
            'media_file': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-gray-300 bg-gray-800 rounded-md p-2 border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Upload a file',
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full rounded-md bg-gray-800 text-gray-300 p-3 border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Write your post here...',
            }),
        }
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email