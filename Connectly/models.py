from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from cloudinary_storage.storage import MediaCloudinaryStorage, RawMediaCloudinaryStorage
from cloudinary_storage.storage import MediaCloudinaryStorage

def upload_location(instance, filename):    #creates a name for a file
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    return f'{timestamp}_{filename}'

def validate_media_file(value):    #checks the type of a file(only images,videos, audios are accepted)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif',  # Image files
                        '.mp4', '.mov', '.avi', '.mkv',  # Video files
                        '.mp3', '.wav', '.ogg']          # Audio files
    if not any(value.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError('Unsupported file extension. Allowed extensions: .jpg, .png, .mp4, .mp3, etc.')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)
    profile_picture = models.ImageField(upload_to=upload_location, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.user.username
def create_profile(sender,instance,created,**kwargs):   #signals, if a user is created a profile is too
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
post_save.connect(create_profile, sender=User)
class Post(models.Model):
    likes = models.ManyToManyField(Profile, related_name='liked', symmetrical=False, blank=True)
    media_file = models.FileField(upload_to=upload_location, validators=[validate_media_file],storage=RawMediaCloudinaryStorage(), blank=False, null=True)
    author = models.ForeignKey(User,related_name='posts', on_delete=models.DO_NOTHING)
    body = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    def num_likes(self):
        return self.likes.count()
    def __str__(self):
        return (f"{self.author}'s post "
                f"{self.body} "
                f"{self.created:%Y-%m-%d-%H:%M}")
    def get_media_type(self):    #in order to understand if its a image, audio or vid
        file_extension = self.media_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif file_extension in ['mp4', 'mov', 'avi', 'mkv']:
            return 'video'
        elif file_extension in ['mp3', 'wav', 'ogg']:
            return 'audio'
        def get_absolute_url(self):
            return self.id

class Comment(models.Model):
    author = models.ForeignKey(Profile,related_name='comments', on_delete=models.CASCADE)
    post= models.ForeignKey(Post,related_name='comments', on_delete=models.CASCADE)
    body = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)