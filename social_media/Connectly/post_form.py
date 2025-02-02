from django import forms
from Connectly.models import Post

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
