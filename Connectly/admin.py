from django.contrib import admin
from Connectly.models import Profile, Post

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)