from django.urls import path, include
from Connectly.views import welcome, profile, follows, followed,home,post_create, login_user, logout_user, register_user

urlpatterns=[
    path('', welcome ,name='welcome'),
    path('profile/<int:user_id>/', profile, name='profile'),
    path('profile/<int:user_id>/audios/', profile, name='audios'),
    path('profile/<int:user_id>/likes/', profile, name='likes'),
    path('profile/<int:user_id>/follows/', follows, name='follows'),
    path('profile/<int:user_id>/followed/', followed, name='followed'),
    path('home/', home, name='home'),
    path('create/', post_create, name='create'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('social-signup/', register_user, name='socialaccount_signup'),
]