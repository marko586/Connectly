from django.urls import path, include
from Connectly.views import welcome, profile, follows, followed,home,post_create, login_user, logout_user

urlpatterns=[
    path('', welcome ,name='welcome'),
    path('profile/<int:id>/', profile, name='profile'),
    path('profile/<int:id>/audios/', profile, name='audios'),
    path('profile/<int:id>/follows/', follows, name='follows'),
    path('profile/<int:id>/followed/', followed, name='followed'),
    path('home/', home, name='home'),
    path('create/', post_create, name='create'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]