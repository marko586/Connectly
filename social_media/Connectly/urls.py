from django.urls import path, include
from Connectly.views import welcome, profile, follows, followed,home,post_create, login_user, logout_user, register_user, verify_otp
from django.contrib.auth import views as auth_views
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
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('password_reset', auth_views.PasswordResetView.as_view(template_name='password_reset_email.html'), name='reset_password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset/cofirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset.html'), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]