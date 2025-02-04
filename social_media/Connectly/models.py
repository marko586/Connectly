from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

import datetime

def upload_location(instance, filename):
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    return f'{timestamp}_{filename}'

def validate_media_file(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif',  # Image files
                        '.mp4', '.mov', '.avi', '.mkv',  # Video files
                        '.mp3', '.wav', '.ogg']          # Audio files
    if not any(value.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError('Unsupported file extension. Allowed extensions: .jpg, .png, .mp4, .mp3, etc.')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)
    bio = models.TextField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to=upload_location, null=True, blank=True)
    def __str__(self):
        return self.user.username
class Post(models.Model):
    likes = models.ManyToManyField(Profile, related_name='liked', symmetrical=False, blank=True)
    media_file = models.FileField(upload_to=upload_location, validators=[validate_media_file], blank=False, null=True)
    author = models.ForeignKey(User,related_name='posts', on_delete=models.DO_NOTHING)
    body = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return (f"{self.author}'s post "
                f"{self.body} "
                f"{self.created:%Y-%m-%d-%H:%M}")
    def get_media_type(self):
        file_extension = self.media_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif file_extension in ['mp4', 'mov', 'avi', 'mkv']:
            return 'video'
        elif file_extension in ['mp3', 'wav', 'ogg']:
            return 'audio'